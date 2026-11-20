# Author: Shriyansh
import json
import random
import re

import joblib

from preprocess import clean_text

THRESHOLD = 0.30
ORDER_ID = re.compile(r"\b(?:ORD)?-?(\d{4,8})\b", re.IGNORECASE)
NEEDS_ORDER_ID = {"order_status", "refund", "cancel_order", "complaint"}

# sample orders, no real database
ORDERS = {
    "12345": ("Shipped", "Arriving in 2 days via BlueDart"),
    "54321": ("Processing", "Packed, will ship within 24 hours"),
    "11111": ("Delivered", "Delivered yesterday at 4:12 PM"),
}

NOT_UNDERSTOOD = [
    "Sorry, I didn't get that. Could you rephrase it? I can help with orders, refunds, shipping, payments and accounts.",
    "I'm not sure what you mean. You can ask about order tracking, refunds, delivery, or ask for a human agent.",
]


class Chatbot:
    def __init__(self):
        self.model = joblib.load("model/intent_model.joblib")
        with open("data/intents.json", encoding="utf-8") as f:
            data = json.load(f)["intents"]
        self.responses = {i["tag"]: i["responses"] for i in data}
        self.waiting_for_id = {}  # session id -> intent we asked the order id for

    def predict(self, text, top=3):
        probs = self.model.predict_proba([clean_text(text)])[0]
        best = probs.argsort()[::-1][:top]
        return [(self.model.classes_[i], float(probs[i])) for i in best]

    def reply(self, text, session="default"):
        text = text.strip()
        if not text:
            return {"reply": "Please type something.", "intent": None, "confidence": 0}

        match = ORDER_ID.search(text)
        order_id = match.group(1) if match else None

        # user is answering our question about the order id
        if order_id and session in self.waiting_for_id:
            intent = self.waiting_for_id.pop(session)
            return self.handle_order(intent, order_id)

        ranked = self.predict(text)
        intent, confidence = ranked[0]
        scores = [{"intent": t, "confidence": round(c, 3)} for t, c in ranked]

        if confidence < THRESHOLD:
            return {"reply": random.choice(NOT_UNDERSTOOD), "intent": "unknown",
                    "confidence": confidence, "scores": scores}

        if intent in NEEDS_ORDER_ID and order_id:
            result = self.handle_order(intent, order_id)
        else:
            if intent in NEEDS_ORDER_ID:
                self.waiting_for_id[session] = intent
            else:
                self.waiting_for_id.pop(session, None)
            result = {"reply": random.choice(self.responses[intent]), "intent": intent}

        result["confidence"] = confidence
        result["scores"] = scores
        return result

    def handle_order(self, intent, order_id):
        status, detail = ORDERS.get(order_id, (None, None))
        if intent == "order_status":
            if status:
                text = f"Order ORD{order_id} is {status}. {detail}."
            else:
                text = f"I couldn't find order ORD{order_id}. Please check the ID and try again."
        elif intent == "refund":
            text = f"I've raised a refund request for order ORD{order_id}. The amount reaches you in 5-7 business days."
        elif intent == "cancel_order":
            if status in ("Shipped", "Delivered"):
                text = f"Order ORD{order_id} is already {status.lower()} so it can't be cancelled. I can start a return instead."
            else:
                text = f"Order ORD{order_id} has been cancelled."
        else:
            text = f"I've escalated order ORD{order_id} as a complaint. Our team will contact you within 24 hours."
        return {"reply": text, "intent": intent, "confidence": 1.0}


if __name__ == "__main__":
    bot = Chatbot()
    while True:
        msg = input("You: ")
        if msg.lower() in ("quit", "exit"):
            break
        out = bot.reply(msg, "cli")
        print("Bot:", out["reply"])
