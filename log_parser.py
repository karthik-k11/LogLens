import re


LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\S+ \S+)\s+(?P<level>INFO|WARNING|ERROR|DEBUG)\s+(?P<message>.*)$"
)


def parse_line(line):
    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None

    return {
        "timestamp": match.group("timestamp"),
        "level": match.group("level"),
        "message": match.group("message"),
    }
def parse_logs(content):
    logs = []

    for line in content.splitlines():
        parsed = parse_line(line)

        if parsed:
            logs.append(parsed)

    return logs

def search_logs(logs, keyword):
    results = []

    for log in logs:
        if keyword.lower() in log["message"].lower():
            results.append(log)

    return results

def filter_by_level(logs, level):
    results = []

    for log in logs:
        if log["level"] == level:
            results.append(log)

    return results

def group_messages(logs):
    groups = {}

    for log in logs:
        message = log["message"]

        if message not in groups:
            groups[message] = 0

        groups[message] += 1

    return groups

