import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

MODEL_PATH = "data/training_data/clause_classifier.joblib"
VECTORIZER_PATH = "data/training_data/tfidf_vectorizer.joblib"

def train_classifier():
    """
    Trains a Logistic Regression model to classify clause types.
    Pipeline: raw text -> TF-IDF vectors -> Logistic Regression -> label
    """
    df = pd.read_csv("data/training_data/clauses.csv")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.25, random_state=42
    )

    # Convert text into numeric vectors (ML models need numbers, not words)
    vectorizer = TfidfVectorizer(stop_words="english")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train a simple, interpretable classifier
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    # Evaluate
    predictions = model.predict(X_test_vec)
    print("=== Model Evaluation ===")
    print(classification_report(y_test, predictions, zero_division=0))

    # Save model + vectorizer so we don't retrain every time
    os.makedirs("data/training_data", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    return model, vectorizer


def load_classifier():
    """Loads the saved model — use this in production instead of retraining"""
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    return model, vectorizer


def predict_clause_type(clause_text, model=None, vectorizer=None):
    """Predicts the type of a single clause"""
    if model is None or vectorizer is None:
        model, vectorizer = load_classifier()

    vec = vectorizer.transform([clause_text])
    prediction = model.predict(vec)[0]
    confidence = max(model.predict_proba(vec)[0])

    return {"clause_type": prediction, "confidence": round(float(confidence), 2)}