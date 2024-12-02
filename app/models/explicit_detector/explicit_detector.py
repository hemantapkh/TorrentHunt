import pickle



class ExplicitDetector:
    def __init__(self, model: str = "GaussianNB.pickle"):
        self.vectorizer = pickle.load(
            open("models/explicit_detector/vectorizer.pickle", "rb"),
        )
        self.model = pickle.load(
            open(f"models/explicit_detector/{model}", "rb"),
        )

    def predict(self, text):
        try:
            vector = self.vectorizer.transform([text]).toarray()
            return self.model.predict(vector)
        except Exception:
            return False
