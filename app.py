from flask import Flask, request, render_template
from log_parser import parse_logs

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

    return str(logs)


if __name__ == "__main__":
    app.run(debug=True)