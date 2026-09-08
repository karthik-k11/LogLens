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

if __name__ == "__main__":
    test_line = "2026-09-08 10:00:00 ERROR Database connection failed"

    result = parse_line(test_line)

    print(result)