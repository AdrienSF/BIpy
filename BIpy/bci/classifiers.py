from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import Pipeline
from mne.decoding import CSP
from BIpy.data_processing import get_sliding_window_partition, LowpassWrapper


class DummyClassifier():
    def __init__(self):
        self.window_size = 1

    def predict_proba(self, data):
        # print('predict_proba:', data)
        return data[0]


# window size in samples, not seconds
def get_trained_CSP_LDA(data, labels, window_size, preprocessing=LowpassWrapper()):

    # slide window over trial data to generate many more data points
    data, labels = get_sliding_window_partition(data, labels, window_size)

    # make pipeline
    preproc = preprocessing
    lda = LinearDiscriminantAnalysis()
    csp = CSP(n_components=10, reg=None, log=None, norm_trace=False, component_order='alternate')
    clf = Pipeline([(str(preproc), preproc), ('CSP', csp), ('LDA', lda)])

    # train model
    clf.fit(data, labels)

    # return trained model
    return clf
