LogLens

LogLens is a lightweight log analysis and incident detection tool built with Python and Flask. It allows users to upload log files, analyze severity levels, detect errors, group repeated messages, and store analysis history in SQLite.

Features

- Upload ".log" and ".txt" files.
- Parse timestamps, severity levels, and log messages.
- Count logs by severity: "INFO", "WARNING", "ERROR", and "DEBUG".
- Search log messages by keyword.
- Filter logs by severity level.
- Group repeated messages and count occurrences.
- Detect incidents by identifying "ERROR" entries.
- Store analysis summaries in SQLite.
- View previous analysis history on the dashboard.

Technology Stack

- Language: Python
- Backend: Flask
- Frontend: HTML
- Database: SQLite
- Parsing: Python regular expressions and file processing

Project Structure

LogLens/
├── app.py
├── log_parser.py
├── detector.py
├── database.py
├── metrics.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
└── templates/
    └── index.html

Requirements

- Python 3.10 or newer
- pip

Installation and Setup

1. Clone the Repository

git clone <your-repository-ssh-url>
cd LogLens

Replace "<your-repository-ssh-url>" with your repository's SSH URL.

2. Create a Virtual Environment

python -m venv venv

3. Activate the Virtual Environment

.\venv\Scripts\Activate.ps1

4. Install Dependencies

pip install -r requirements.txt

Ensure "requirements.txt" contains Flask and any other dependencies used by the project.

Running the Application

1. Initialize the Database

python database.py

2. Start the Flask Server

python app.py

3. Open the Dashboard

Visit:

http://127.0.0.1:5000

Upload a ".log" or ".txt" file to view its analysis.

Supported Log Format

Log entries currently follow this format:

YYYY-MM-DD HH:MM:SS LEVEL Message text

Example:

2026-10-08 10:00:00 INFO Application started
2026-10-08 10:01:00 WARNING Memory usage is high
2026-10-08 10:02:00 ERROR Database connection failed
2026-10-08 10:03:00 DEBUG Checking database status

Supported severity levels:

- "INFO"
- "WARNING"
- "ERROR"
- "DEBUG"

Lines that do not match the parser's expected format may be skipped.

Database

LogLens uses SQLite to store analysis history.

The "analysis_history" table stores:

- Uploaded filename
- INFO count
- WARNING count
- ERROR count
- DEBUG count

The database file, "loglens.db", is generated locally. It should not be committed to GitHub.

Add this entry to ".gitignore":

loglens.db

Commit "database.py" to GitHub, but keep the generated database file local.

Current Limitations

- Each "ERROR" entry is currently treated as an incident.
- Repeated-message grouping compares message text exactly.
- The parser expects a specific timestamp and severity format.
- The application is designed for local use and does not require AI APIs or cloud services.

Future Improvements

- Add interactive search and severity filters to the dashboard.
- Improve invalid-file handling and input validation.
- Enhance the dashboard design and user experience.
- Add automated tests for parsing, metrics, incident detection, and database operations.