from flask import Flask, request, render_template
from log_parser import parse_logs
from metrics import count_levels
from detector import detect_incidents
from database import init_db, save_analysis, get_history

app = Flask(__name__)


@app.route("/")
def home():
    history = get_history()

    return render_template(
        "index.html",
        history=history
    )


@app.route("/upload", methods=["POST"])
def upload_log():
    file = request.files.get("file")

    if not file:
        return "No file uploaded", 400

    content = file.read().decode("utf-8")

    logs = parse_logs(content)

    counts = count_levels(logs)

    save_analysis(file.filename, counts)

    incidents = detect_incidents(logs)

    history = get_history()

    return render_template(
        "index.html",
        counts=counts,
        incidents=incidents,
        history=history
    )

init_db()
if __name__ == "__main__":
    app.run(debug=True)