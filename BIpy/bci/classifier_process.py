from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_byprop
from multiprocessing import Process
from inlets import WindowInlet
import numpy as np

import time

def run_classifier(clf, in_source_id='myuid323457', out_source_id='classifier_output', stream_no=0, window_size=None):
    """Runs a real-time classifier untill killed

    Parameters
    ----------
    clf : object implementing predict_proba(data)
        Classifier to run. Must be able to take the output of WindowInlet.pull_window() as input to clf.predict_proba(), 
        and clf.predict_proba(data) must output a single float
    in_source_id : str
        Pylsl stream source_id of incoming data to be fed to the classifier
            Default myuid323457 - dry EEG, for ActiChamp use 17010768
    out_source_id : str, default 'classifier_output'
        Pylsl stream source_id for output of the classifier
        
    strem_no : int
        Index of the stream. Should be 0 or 1, ask Tian for help on this
        Default 0
    window_size : int,  default None
        Number of samples required as input to the provided classifier clf
        If None, the function will attenpt to get this from clf.window_size


    Output
    ------
    For every input recieved, immediately pushes the provided classifiers output (predict_proba(data)) to lsl
    """

    print('classifier process starting...')
    if not window_size:
        if hasattr(clf, 'window_size') and clf.window_size:
            window_size = clf.window_size
        else:
            raise ValueError('Window size must be specified when creating ClassifierProcess if the classifier does not have a window_size attribute.')
    print('making window inlet')
    winlet = WindowInlet(in_source_id, window_size=window_size, stream_no=stream_no)

    print('creating stream \"'+str(out_source_id)+'\"...')
    info = StreamInfo(source_id=out_source_id)
    outlet = StreamOutlet(info)
    print('done')

    # only start the predictions once the window inlet has enough data buffered
    while len(winlet.pull_window()) < window_size: #[NOTE]: add timeout condition
        pass

    while True:
        pulled = winlet.pull_window()
        # print('clf input shape:', np.array(pulled).shape)
        proba = clf.predict_proba(pulled)
        # print('proba:', proba)
        outlet.push_sample([proba])



def ClassifierProcess(clf, in_source_id='myuid323457', out_source_id='classifier_output', stream_no=0, window_size=500):
    """Returns a multiprocessing.process of run_classifier
    
    Parameters
    ----------
    clf : object implementing predict_proba(data)
        Classifier to run
    in_source_id : str
        Pylsl stream source_id of incoming data to be fed to the classifier
            Default myuid323457 - dry EEG, for ActiChamp use 17010768
    out_source_id : str
        Pylsl stream source_id for output of the classifier
        Default 'classifier_output'
    strem_no : int
        Index of the stream. Should be 0 or 1, ask Tian for help on this
        Default 0
    window_size : int
        Number of samples required as input to the provided classifier clf
        If None, the function will attenpt to get this from clf.window_size
        Default None

    Output
    ------
    multiprocessing.process() of BIpy.classifier_process.run_classifier()
    
    """

    return Process(target=run_classifier, args=(clf, in_source_id, out_source_id, stream_no, window_size))