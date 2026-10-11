import csv
import io
import json

from flask import Flask, Response, flash, redirect, render_template, request, session, url_for

from database import get_history, init_db, save_analysis
from detector import detect_incidents
from log_parser import filter_by_level, group_messages, parse_logs, search_logs, sort_logs
from metrics import count_levels

app = Flask(__name__)
app.config["SECRET_KEY"] = "loglens-production-key"


def set_session_analysis(filename, logs, counts, incidents, groups):
    session["last_filename"] = filename
    session["last_logs"] = logs
    session["last_counts"] = counts
    session["last_incidents"] = incidents
    session["last_groups"] = groups


def get_filtered_logs():
    keyword = (request.args.get("keyword") or "").strip()
    level = (request.args.get("level") or "ALL").upper().strip()
    sort_by = (request.args.get("sort_by") or "timestamp").lower()
    sort_order = (request.args.get("sort_order") or "desc").lower()
    try:
        page = max(int(request.args.get("page") or 1), 1)
    except (TypeError, ValueError):
        page = 1
    page_size = 25

    logs = session.get("last_logs") or []
    filtered_logs = list(logs)
    if keyword:
        filtered_logs = search_logs(filtered_logs, keyword)
    if level and level != "ALL":
        filtered_logs = filter_by_level(filtered_logs, level)

    filtered_logs = sort_logs(filtered_logs, sort_by=sort_by, sort_order=sort_order)
    total_pages = max(1, (len(filtered_logs) + page_size - 1) // page_size)
    page = min(page, total_pages)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_logs = filtered_logs[start:end]

    return logs, paginated_logs, filtered_logs, keyword, level, sort_by, sort_order, page, total_pages


def build_dashboard_context():
    history = get_history(limit=10)
    logs, paginated_logs, filtered_logs, keyword, level, sort_by, sort_order, page, total_pages = get_filtered_logs()
    counts = session.get("last_counts")
    incidents = session.get("last_incidents")
    groups = session.get("last_groups")
    filename = session.get("last_filename")

    return {
        "history": history,
        "counts": counts,
        "incidents": incidents,
        "groups": groups,
        "filename": filename,
        "filtered_logs": paginated_logs,
        "filter_keyword": keyword,
        "filter_level": level,
        "total_entries": len(logs),
        "filtered_count": len(filtered_logs),
        "sort_by": sort_by,
        "sort_order": sort_order,
        "page": page,
        "total_pages": total_pages,
        "query_string": request.query_string.decode("utf-8"),
    }


@app.route("/")
def home():
    return render_template("index.html", **build_dashboard_context())


@app.route("/export")
def export_logs():
    filename = session.get("last_filename") or "loglens-export"
    logs = session.get("last_logs") or []
    _, _, filtered_logs, keyword, level, _, _, _, _ = get_filtered_logs()

    export_format = (request.args.get("format") or "csv").lower()
    export_rows = filtered_logs if keyword or level != "ALL" else logs

    if export_format == "json":
        payload = json.dumps(export_rows, indent=2)
        return Response(
            payload,
            mimetype="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}.json"'},
        )

    fieldnames = ["timestamp", "level", "message"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in export_rows:
        writer.writerow({
            "timestamp": row.get("timestamp", ""),
            "level": row.get("level", ""),
            "message": row.get("message", ""),
        })

    content = output.getvalue()
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}.csv"'},
    )


@app.route("/upload", methods=["POST"])
def upload_log():
    file = request.files.get("file")

    if not file or file.filename == "":
        flash("Please choose a log file before uploading.", "error")
        return redirect(url_for("home"))

    try:
        content = file.read().decode("utf-8")
    except UnicodeDecodeError:
        flash("The uploaded file is not valid UTF-8 text. Please upload a plain text log file.", "error")
        return redirect(url_for("home"))

    logs = parse_logs(content)
    if not logs:
        flash("No valid log entries were found in the uploaded file.", "warning")
        return redirect(url_for("home"))

    counts = count_levels(logs)
    incidents = detect_incidents(logs)
    groups = group_messages(logs)
    save_analysis(file.filename, counts)
    set_session_analysis(file.filename, logs, counts, incidents, groups)

    return redirect(url_for("home"))


init_db()


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)