import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from preprocess import clean_text

with open("data/intents.json", encoding="utf-8") as f:
    intents = json.load(f)["intents"]

texts, labels = [], []
for intent in intents:
    for pattern in intent["patterns"]:
        texts.append(clean_text(pattern))
        labels.append(intent["tag"])

print("phrases:", len(texts), " intents:", len(set(labels)))

features = FeatureUnion([
    ("word", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
    ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True)),
])
model = Pipeline([
    ("features", features),
    ("clf", LogisticRegression(C=12, max_iter=2000, class_weight="balanced")),
])

x_train, x_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)
model.fit(x_train, y_train)
pred = model.predict(x_test)
print(classification_report(y_test, pred, zero_division=0))
accuracy = (pred == y_test).mean() if hasattr(pred, "mean") else sum(p == t for p, t in zip(pred, y_test)) / len(y_test)
print("test accuracy: %.3f" % accuracy)

# final model uses all the data
model.fit(texts, labels)
joblib.dump(model, "model/intent_model.joblib")
with open("model/info.json", "w") as f:
    json.dump({"phrases": len(texts), "intents": len(set(labels)), "test_accuracy": round(float(accuracy), 3)}, f)
print("model saved")
