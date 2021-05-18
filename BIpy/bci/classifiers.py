
class DummyClassifier():
    def __init__(self):
        self.window_size = 1

    def predict_proba(self, data):
        print('predict_proba:', data)
        return data[0]