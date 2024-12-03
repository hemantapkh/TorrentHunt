import joblib

class ExplicitDetector:
    def __init__(self, model: str = "RandomForest.joblib"):
        self.vectorizer = joblib.load(
            open("models/explicit_detector/vectorizer.joblib", "rb"),
        )
        self.model = joblib.load(
            open(f"models/explicit_detector/{model}", "rb"),
        )

    def predict(self, text):
        try:
            vector = self.vectorizer.transform([text])
            return bool(self.model.predict(vector)[0])
        except Exception:
            return False
