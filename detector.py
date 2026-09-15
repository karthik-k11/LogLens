def detect_incidents(logs):
    incidents = []

    for log in logs:
        if log["level"] == "ERROR":
            incidents.append(log)

    return incidents


if __name__ == "__main__":
    test_logs = [
        {"level": "INFO", "message": "Application started"},
        {"level": "ERROR", "message": "Database connection failed"},
        {"level": "WARNING", "message": "Memory usage is high"},
        {"level": "ERROR", "message": "Server connection failed"}
    ]

    result = detect_incidents(test_logs)

    for incident in result:
        print(incident)