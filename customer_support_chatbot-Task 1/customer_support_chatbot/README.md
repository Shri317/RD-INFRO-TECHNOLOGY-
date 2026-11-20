# Customer Support Chatbot

Author: Shriyansh

A chatbot that answers customer support questions (orders, refunds, shipping, payments, account problems) using NLP intent classification, with a small Flask web interface.

## Technologies
Python, NLTK, scikit-learn, Flask, HTML/CSS/JavaScript

## How it works
1. `data/intents.json` holds the training phrases and replies for 15 intents.
2. `preprocess.py` lowercases the text, removes punctuation and common words, and stems each word.
3. `train.py` converts the phrases to TF-IDF features (word and character n-grams) and trains a Logistic Regression classifier. Accuracy on a held-out 20% split is about 77%.
4. `chatbot.py` predicts the intent of a message, picks the extracted order ID if there is one, and remembers when it has asked for an order ID so the next message can be the answer. Low-confidence messages get a "didn't understand" reply.
5. `app.py` is the Flask server and `templates/` + `static/` hold the chat page.

## Files
```
data/intents.json
preprocess.py
train.py
chatbot.py
app.py
templates/index.html
static/style.css, static/script.js
tests/test_chatbot.py
```

## Notes
- The orders (ORD12345, ORD54321, ORD11111) are sample data, there is no real database.
- The model is small, so more training phrases in `intents.json` would improve it.
