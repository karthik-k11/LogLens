def count_levels(logs):
    counts = {
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "DEBUG": 0,
    }

    for log in logs:
        level = str(log.get("level", "")).upper().strip()
        if level in counts:
            counts[level] += 1

    return counts


if __name__ == "__main__":
    test_logs = [
        {"level": "INFO"},
        {"level": "ERROR"},
        {"level": "INFO"},
        {"level": "WARNING"},
        {"level": "ERROR"},
    ]

    print(count_levels(test_logs))