# Author: Shriyansh
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from chatbot import Chatbot

bot = Chatbot()


def test_intents():
    cases = {
        "hello there": "greeting",
        "where is my order": "order_status",
        "i want my money back": "refund",
        "please cancel my order": "cancel_order",
        "what payment methods do you accept": "payment",
        "i forgot my password": "account_issue",
        "thank you so much": "thanks",
    }
    for text, expected in cases.items():
        assert bot.predict(text)[0][0] == expected, text


def test_order_followup():
    bot.reply("where is my order", "t1")
    out = bot.reply("ORD12345", "t1")
    assert "Shipped" in out["reply"]


def test_unknown_message():
    assert bot.reply("zxqv blorp wibble", "t2")["intent"] == "unknown"


def test_empty_message():
    assert bot.reply("   ", "t3")["intent"] is None


def test_web_routes():
    from app import app
    client = app.test_client()
    assert client.get("/").status_code == 200
    assert client.post("/chat", json={"message": "hi"}).status_code == 200
    assert client.post("/chat", json={}).status_code == 400
