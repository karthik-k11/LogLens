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

if __name__ == "__main__":
    test_content = """2026-09-08 10:00:00 INFO Application started
2026-09-08 10:01:00 WARNING Memory usage is high
2026-09-08 10:02:00 ERROR Database connection failed
2026-09-08 10:03:00 INFO Application stopped"""

    result = parse_logs(test_content)

    for log in result:
        print(log)