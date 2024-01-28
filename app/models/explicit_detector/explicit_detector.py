import pickle

vectorizer = pickle.load(
    open("models/explicit_detector/vectorizer.pickle", "rb"),
)
model = pickle.load(
    open("models/explicit_detector/RandomForestClassifier.pickle", "rb"),
)


class ExplicitDetector:
    def __init__(self):
        pass

    def predict(self, text):
        vector = vectorizer.transform([text]).toarray()
        return model.predict(vector)
