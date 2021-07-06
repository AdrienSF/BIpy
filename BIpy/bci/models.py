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
    """Wrapper class for using an sklearn csp+lda pipeline in a BIpy.bci.ClassifierProcess

    Methods
    -------
    predict_proba(self, window: np.array)
        takes the output form a WindowInlet and returns the probability (according to the csp+lda classifier) that the right hand was imagined
    def fit(self, data, labels):
        calls fit(data, labels) on the csp+lda classifier
    
    """    

    def __init__(self, data_channels=list(range(20)), window_size=1000, preprocessing=LowpassWrapper()):
        """
            Parameters
            ----------
            data_channels : int, default list(range(20))
                Channels that the classifier should use as input
            window_size : int, default 1000
                number of samples of eeg data the classifier should use as input
            preprocessing : default LowpassWrapper()
                Step added to the start of the csp+lda sklearn pipeline
        """
        
        self.window_size=window_size
        self.data_channels = data_channels

        # make pipeline
        preproc = preprocessing
        lda = LinearDiscriminantAnalysis()
        csp = CSP(n_components=10, reg=None, log=None, norm_trace=False, component_order='alternate')
        self.clf = Pipeline([(str(preproc), preproc), ('CSP', csp), ('LDA', lda)])

    def predict_proba(self, window: np.array):
        """takes the output form a WindowInlet and returns the probability (according to the csp+lda classifier) that the right hand was imagined"""
        
        data = np.transpose(np.array(window))[self.data_channels]
        # print('data shape in wrapped:', data.shape)
        proba = self.clf.predict_proba([data])
        return proba[0][1] # proba = [[prob_left, prob_right]]


    def fit(self, data, labels):
        """calls fit(data, labels) on the csp+lda classifier"""
        self.clf.fit(data, labels)
        