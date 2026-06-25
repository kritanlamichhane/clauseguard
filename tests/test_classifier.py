import sys
sys.path.append(".")

from backend.classifier import train_classifier, predict_clause_type

# Train the model (only need to do this once, then it's saved)
model, vectorizer = train_classifier()

# Try it on a brand new clause it's never seen
test_clause = "The Company may terminate this Agreement immediately if Contractor breaches any material term."
result = predict_clause_type(test_clause, model, vectorizer)
print(f"\nPrediction for new clause: {result}")