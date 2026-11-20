import re

from nltk.stem import PorterStemmer

stemmer = PorterStemmer()
STOP_WORDS = {"the", "a", "an", "please", "of", "and"}


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    words = [w for w in text.split() if w not in STOP_WORDS]
    return " ".join(stemmer.stem(w) for w in words)
