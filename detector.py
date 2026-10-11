def detect_incidents(logs, limit=10):
    incidents = []

    for log in logs:
        if log.get("level") == "ERROR":
            incidents.append({
                "level": "ERROR",
                "message": log.get("message", "Unknown error"),
                "timestamp": log.get("timestamp", "Unknown time"),
            })

    return incidents[:limit]


if __name__ == "__main__":
    test_logs = [
        {"level": "INFO", "message": "Application started"},
        {"level": "ERROR", "message": "Database connection failed"},
        {"level": "WARNING", "message": "Memory usage is high"},
        {"level": "ERROR", "message": "Server connection failed"},
    ]

    for incident in detect_incidents(test_logs):
        print(incident)