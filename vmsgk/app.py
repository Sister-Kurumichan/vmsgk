from flask import Flask, request, jsonify, render_template
from chat import get_reply

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    reply = get_reply(user_message)

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)