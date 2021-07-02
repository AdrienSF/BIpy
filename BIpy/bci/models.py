from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import Pipeline
from mne.decoding import CSP
from BIpy.data_processing import get_sliding_window_partition, LowpassWrapper

import numpy as np

class DummyClassifier():
    """Dummy classifier for testing purpose"""
    def __init__(self):
        self.window_size = 1

    def predict_proba(self, data):
        """returns input[0]"""
        # print('predict_proba:', data)
        return data[0]


# window size in samples, not seconds
def get_trained_CSP_LDA(data, labels, window_size=None, preprocessing=LowpassWrapper()):
    """Returns a trained sklearn pipeline of [csp, lda]

    Parameters
    ----------
    data : np.array
        Data to train the classifier on
        Shape (trials, channels, time)
    labels : np.array
        1d array of labels to the training data
    window_size : int
        Size in samples (not seconds) the classifier should be trained on
        If None, the function will trian with each entire trial as input
        Default None
    preprocessing : object implementing fit_transform and transform
        Preprocessing step to add at the beggining of the sklearn pipeline
        Default BIpy.preprocessing.LowpassWraspper()

    Returns
    -------
    clf
        A trained csp + lda Pipeline
    """

    if window_size == None:
        window_size = data.shape[-1]

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


# [NOTE]: extend this so it generalizes to gell eeg
class WrappedCSPLDAClassifier():
    def __init__(self, window_siz=1000, preprocessing=LowpassWrapper()):
        self.window_siz=1000

        # make pipeline
        preproc = preprocessing
        lda = LinearDiscriminantAnalysis()
        csp = CSP(n_components=10, reg=None, log=None, norm_trace=False, component_order='alternate')
        self.clf = Pipeline([(str(preproc), preproc), ('CSP', csp), ('LDA', lda)])

    def predict_proba(self, window):
        data = np.transpose(np.array(window))[:20]
        # print('data shape in wrapped:', data.shape)
        proba = self.clf.predict_proba([data])
        return proba[0][1] # proba = [[prob_left, prob_right]]


    def fit(self, data, labels): # [NOTE]: wrap input here as well?
        self.clf.fit(data, labels)