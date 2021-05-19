from sklearn.lda import LDA
from mne.decoding import CSP
from BIpy.bci.data_processing import get_sliding_window_partition, organize_data


class DummyClassifier():
    def __init__(self):
        self.window_size = 1

    def predict_proba(self, data):
        # print('predict_proba:', data)
        return data[0]



def get_trained_CSP_LDA(raw_data, window_size):
    # somehow label and organize data
    data, labels = organize_data(raw_data)

    # ########

    # slide window over trial data to generate many more data points
    data, labels = get_sliding_window_partition(data, lables)

    # make pipeline
    lda = LDA()
    csp = CSP(n_components=4, reg=None, log=True)
    clf = Pipeline([('CSP', csp), ('LDA', lda)])

    # train model
    clf.fit(data, labels)
    # clf.fit_transform(data, labels) ?

    # return trained model
    return clf
