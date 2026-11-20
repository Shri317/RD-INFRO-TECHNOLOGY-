import uuid

from flask import Flask, jsonify, render_template, request, session

from chatbot import Chatbot

app = Flask(__name__)
app.secret_key = "change-this-key"
bot = Chatbot()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "empty message"}), 400
    if len(message) > 500:
        return jsonify({"error": "message too long"}), 400
    session.setdefault("sid", uuid.uuid4().hex)
    return jsonify(bot.reply(message, session["sid"]))


@app.route("/reset", methods=["POST"])
def reset():
    bot.waiting_for_id.pop(session.get("sid"), None)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=False)
