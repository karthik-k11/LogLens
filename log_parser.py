import re


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+\s+\S+)\s+(?P<level>INFO|WARNING|ERROR|DEBUG)\s+(?P<message>.*)$"
)


def parse_line(line):
    cleaned = (line or "").strip()
    if not cleaned:
        return None

    match = LOG_PATTERN.match(cleaned)
    if not match:
        return None

    return {
        "timestamp": match.group("timestamp"),
        "level": match.group("level").upper(),
        "message": match.group("message").strip(),
    }


def parse_logs(content):
    if not content:
        return []

    logs = []
    for line in content.splitlines():
        parsed = parse_line(line)
        if parsed:
            logs.append(parsed)
    return logs


def search_logs(logs, keyword):
    keyword = (keyword or "").lower().strip()
    if not keyword:
        return []

    return [
        log for log in logs if keyword in str(log.get("message", "")).lower()
    ]


def filter_by_level(logs, level):
    target = (level or "").upper().strip()
    return [log for log in logs if str(log.get("level", "")).upper() == target]


def group_messages(logs):
    groups = {}

    for log in logs:
        message = str(log.get("message", "")).strip()
        if not message:
            continue
        groups[message] = groups.get(message, 0) + 1

    return dict(sorted(groups.items(), key=lambda item: (-item[1], item[0])))


def sort_logs(logs, sort_by="timestamp", sort_order="desc"):
    sort_by = (sort_by or "timestamp").lower()
    sort_order = (sort_order or "desc").lower()
    reverse = sort_order == "desc"

    if sort_by == "level":
        order = {"INFO": 1, "WARNING": 2, "ERROR": 3, "DEBUG": 4}
        return sorted(logs, key=lambda log: (order.get(str(log.get("level", "")).upper(), 99), str(log.get("timestamp", ""))), reverse=reverse)

    if sort_by == "message":
        return sorted(logs, key=lambda log: str(log.get("message", "")).lower(), reverse=reverse)

    return sorted(logs, key=lambda log: str(log.get("timestamp", "")), reverse=reverse)


if __name__ == "__main__":
    test_content = """2026-09-08 10:00:00 ERROR Database connection failed
2026-09-08 10:01:00 ERROR Database connection failed
2026-09-08 10:02:00 ERROR Server connection failed
2026-09-08 10:03:00 INFO Application started"""

    logs = parse_logs(test_content)
    print(group_messages(logs))