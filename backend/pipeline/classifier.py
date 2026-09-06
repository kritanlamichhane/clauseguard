import os
import joblib
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from backend.core.config import DATA_DIR

MODEL_PATH = os.path.join(DATA_DIR, "training_data", "clause_classifier.joblib")
VECTORIZER_PATH = os.path.join(DATA_DIR, "training_data", "tfidf_vectorizer.joblib")
TRAINING_CSV = os.path.join(DATA_DIR, "training_data", "clauses.csv")


def train_classifier():
    """
    Trains a Logistic Regression model to classify clause types.
    Pipeline: raw text -> TF-IDF vectors -> Logistic Regression -> label
    """
    if not os.path.exists(TRAINING_CSV):
        raise FileNotFoundError(f"Training dataset not found at {TRAINING_CSV}")

    df = pd.read_csv(TRAINING_CSV)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.25, random_state=42
    )

    vectorizer = TfidfVectorizer(stop_words="english")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    predictions = model.predict(X_test_vec)
    print("=== Model Evaluation ===")
    print(classification_report(y_test, predictions, zero_division=0))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    return model, vectorizer


def load_classifier() -> Tuple[Optional[LogisticRegression], Optional[TfidfVectorizer]]:
    """Loads the saved model and vectorizer from disk"""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        return None, None
    try:
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        return model, vectorizer
    except Exception as e:
        print(f"[WARNING] classifier.py: Could not load trained classifier: {e}")
        return None, None


def predict_clause_type(clause_text: str, model=None, vectorizer=None) -> Dict[str, Any]:
    """Predicts the type of a single clause"""
    if model is None or vectorizer is None:
        model, vectorizer = load_classifier()

    if model is None or vectorizer is None:
        return {"clause_type": "General", "confidence": 0.0}

    try:
        vec = vectorizer.transform([clause_text])
        prediction = model.predict(vec)[0]
        confidence = max(model.predict_proba(vec)[0])
        return {"clause_type": prediction, "confidence": round(float(confidence), 2)}
    except Exception as e:
        print(f"[WARNING] classifier.py: Prediction failed: {e}")
        return {"clause_type": "General", "confidence": 0.0}
