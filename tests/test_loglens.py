import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import database
from app import app
from detector import detect_incidents
from log_parser import group_messages, parse_logs, search_logs, sort_logs
from metrics import count_levels


class LogLensTests(unittest.TestCase):
    def setUp(self):
        self.database_file = tempfile.NamedTemporaryFile(delete=False)
        self.database_file.close()
        self.database_path = patch.object(database, "DATABASE", self.database_file.name)
        self.database_path.start()
        database.init_db()
        app.config.update(TESTING=True, SECRET_KEY="test-secret", MAX_CONTENT_LENGTH=10 * 1024 * 1024)
        self.client = app.test_client()

    def tearDown(self):
        self.database_path.stop()
        os.unlink(self.database_file.name)

    def test_parser_metrics_incidents_and_groups(self):
        logs = parse_logs(
            "\ufeff2026-10-20 10:00:00 INFO Started\n"
            "invalid entry\n"
            "2026-10-20 10:01:00 ERROR Failed\n"
            "2026-10-20 10:02:00 ERROR Failed\n"
        )

        self.assertEqual(len(logs), 3)
        self.assertEqual(count_levels(logs), {"INFO": 1, "WARNING": 0, "ERROR": 2, "DEBUG": 0})
        self.assertEqual(len(detect_incidents(logs)), 2)
        self.assertEqual(group_messages(logs)["Failed"], 2)
        self.assertEqual(search_logs(logs, "fail"), logs[1:])
        self.assertEqual(sort_logs(logs, "timestamp", "asc"), logs)

    def test_upload_persists_logs_outside_the_session_and_renders_dashboard(self):
        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(
                b"2026-10-20 10:00:00 INFO Started\n"
                b"2026-10-20 10:01:00 ERROR Failed\n"
                b"2026-10-20 10:02:00 ERROR Failed\n"
            ), "sample.log")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 302)
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn(b"Repeated messages", page.data)
        self.assertIn(b"2\xc3\x97", page.data)
        self.assertIn(b"sample.log", page.data)
        with self.client.session_transaction() as session_data:
            self.assertIn("analysis_id", session_data)
            self.assertNotIn("last_logs", session_data)
        self.assertEqual(len(database.get_logs(session_data["analysis_id"])), 3)

    def test_large_upload_uses_a_small_session_and_paginates(self):
        content = "".join(
            f"2026-10-20 10:{index // 60:02d}:{index % 60:02d} INFO Entry {index}\n"
            for index in range(100)
        ).encode()
        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(content), "large.log")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 302)
        self.assertLess(len(response.headers["Set-Cookie"]), 4093)
        page = self.client.get("/")
        self.assertIn(b"1 / 4", page.data)
        self.assertIn(b"Entry 99", page.data)
        self.assertNotIn(b"Entry 0", page.data)

    def test_filter_and_json_export(self):
        self.client.post(
            "/upload",
            data={"file": (io.BytesIO(
                b"2026-10-20 10:00:00 INFO Started\n"
                b"2026-10-20 10:01:00 ERROR Failed\n"
            ), "sample.log")},
            content_type="multipart/form-data",
        )

        response = self.client.get("/export?format=json&level=ERROR")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [{
            "timestamp": "2026-10-20 10:01:00",
            "level": "ERROR",
            "message": "Failed",
        }])

        csv_response = self.client.get("/export?format=csv&keyword=Fail&level=ERROR")
        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(
            csv_response.data.decode(),
            "timestamp,level,message\r\n2026-10-20 10:01:00,ERROR,Failed\r\n",
        )

    def test_dashboard_export_links_preserve_active_filters(self):
        self.client.post(
            "/upload",
            data={"file": (io.BytesIO(
                b"2026-10-20 10:00:00 INFO Started\n"
                b"2026-10-20 10:01:00 ERROR Failed\n"
            ), "sample.log")},
            content_type="multipart/form-data",
        )

        page = self.client.get("/?keyword=Fail&level=ERROR")

        self.assertIn(b"/export?format=csv&amp;keyword=Fail&amp;level=ERROR", page.data)
        self.assertIn(b"/export?format=json&amp;keyword=Fail&amp;level=ERROR", page.data)

    def test_rejects_unsupported_file_extension(self):
        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"log data"), "notes.csv")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        self.assertIn(b"Please upload a .log, .txt, or .out file.", response.data)
        self.assertEqual(database.get_history(), [])

    def test_rejects_invalid_utf8_and_logs_without_valid_entries(self):
        invalid_utf8 = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"\xff"), "broken.log")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        invalid_log = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"not a valid entry\n"), "broken.log")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        self.assertIn(b"not valid UTF-8", invalid_utf8.data)
        self.assertIn(b"No valid log entries", invalid_log.data)
        self.assertEqual(database.get_history(), [])

    def test_rejects_uploads_over_size_limit(self):
        app.config["MAX_CONTENT_LENGTH"] = 32
        response = self.client.post(
            "/upload",
            data={"file": (io.BytesIO(b"x" * 100), "large.log")},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        self.assertIn(b"Maximum file size is 10 MB", response.data)
        app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


if __name__ == "__main__":
    unittest.main()
