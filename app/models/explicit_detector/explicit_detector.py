from pathlib import Path

import joblib

MODEL_DIR = Path(__file__).resolve().parent


class ExplicitDetector:
    def __init__(self, model: str = "RandomForest.joblib"):
        self.vectorizer = joblib.load(MODEL_DIR / "vectorizer.joblib")
        self.model = joblib.load(MODEL_DIR / model)

    def predict(self, text):
        try:
            vector = self.vectorizer.transform([text])
            return bool(self.model.predict(vector)[0])
        except Exception:
            return False
