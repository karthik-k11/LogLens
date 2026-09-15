from flask import Flask, request, render_template
from log_parser import parse_logs
from metrics import count_levels
from detector import detect_incidents

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_log():
    file = request.files.get("file")

    if not file:
        return "No file uploaded", 400

    content = file.read().decode("utf-8")

    logs = parse_logs(content)

    counts = count_levels(logs)

    incidents = detect_incidents(logs)

    return render_template(
        "index.html",
        counts=counts,
        incidents=incidents
    )


if __name__ == "__main__":
    app.run(debug=True)