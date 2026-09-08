from flask import Flask, request, render_template


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

    return content


if __name__ == "__main__":
    app.run(debug=True)