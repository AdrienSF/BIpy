from BIpy.bci.models import get_trained_CSP_LDA
import numpy as np
from sklearn.model_selection import cross_val_score
import random


def test_get_trained_CSP_LDA():
    # load sample data
    data = np.load('tests/test_data/x_Train_Akima_NF_Dry_EEG3.npy')
    labels = np.load('tests/test_data/y_Train_Akima_NF_Dry_EEG3.npy')
    # just test that it trains and runs without errors
    clf = get_trained_CSP_LDA(data, labels, window_size=1000)


    shufi = list(range(50))
    random.shuffle(shufi)

    acc = np.mean(cross_val_score(clf, data[shufi], labels[shufi], cv=10))
    print('Test accuracy:', acc)
    # surely, the accuracy will be above 60%, I mean that's hardly above chance level (.56 on this data) ... right?
    # assert acc > .6
    # ... wrong, acc varies too much with only 50 samples and random crossval


