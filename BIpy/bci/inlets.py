from pylsl import StreamInlet, resolve_byprop
import numpy as np
from time import sleep, time

class WindowInlet():
    """A class used like a pylsl inlet, but that returns window_size past samples on each pull_window
    Attributes
    ----------
    inlet : pylsl.StreamInlet
        Pylsl inlet from which real-time EEG data is pulled
    window_size : int
        Width in samples (not seconds) of the sliding window
    window : list
        List of window_size last samples pulled from inlet


    Methods
    -------
    pull_window
        Pulls the last window_size from inlet
    
    """

    def __init__(self, source_id='myuid323457', stream_no=0, window_size=500):
        """
        Parameters        
        ----------
            source_id : str
                Pylsl stream source_id of incoming data buffered for sliding window
                Default myuid323457 - dry EEG, for ActiChamp use 17010768
            stream_no : int
                Index of the stream. Should be 0 or 1, ask Tian for help on this
                Default 0
            window_size : int
                Number of past samples returned on call of pull_window
                Default 500
            transpose_output : bool, default True
                If True transposes the output of the window so that it has the shape expected by mne's CSP

        """

        print("looking for stream \"" + str(source_id) + "\"...")
        streams = resolve_byprop('source_id', source_id, timeout=5) # for ActiChamp - 17010768 ||||| portable: myuid323457
        if not streams:
            raise TimeoutError('Stream \"' + str(source_id) + '\" not found, timeout expired.')

        self.inlet = StreamInlet(streams[stream_no]) # for ActiChamp (I think streams[1]) |||| streams[0] for portable
        print('found')

        self.window_size = window_size
        self.window = []

        self.pull_window()



    def pull_window(self, window_size=None, timeout=0.25):
        """Pulls the last window_size samples from inlet

        Parameters
        ----------
        window_size : int
            Width in samples (not seconds) of the sliding window
            If None, uses self.window_siz, Default None
        timeout : float
            Timeout in seconds passed to pylsl.inlet.pull_chunk
            Default .25

        Returns
        -------
        window : list, shape: (window_size, channels)
            list of window_size last samples pulled from inlet
        """

        if not window_size:
            window_size = self.window_size
        # should take all buffered data
        chunk = self.inlet.pull_chunk(timeout=timeout, max_samples=10000)[0]
        # chunk = self.inlet.pull_sample()[0]
        # if no data is buffered, return
        if not chunk:
            return
        # print('len chunk:', len(chunk))
        self.window = self.window + chunk
        # print('window shape:', np.array(self.window).shape)

        # trim to window size
        if len(self.window) > self.window_size:
            excess = len(self.window) - self.window_size
            self.window = self.window[excess:]


        # print('window shape:', np.array(self.window).shape)
        return self.window




class ClassifierInlet():
    """A class used like a pylsl inlet, but made for getting the output of a real-time classifier

    Attributes
    ----------
    inlet : pylsl.StreamInlet
        Pylsl inlet from which the output of a classifier is pulled

    Methods
    -------
    pull_sample
        returns inlet.pull_sample()
    """

    def __init__(self, source_id='classifier_output'):
        """
        Parameters
        ----------
        source_id : str
            Pylsl stream source_id for incoming data
            Default 'classifier_output'
        """
        print("looking for stream \"" + str(source_id) + "\"...")
        streams = resolve_byprop('source_id', source_id, timeout=5)
        if not streams:
            raise TimeoutError('Stream \"' + str(source_id) + '\" not found, timeout expired.')

        self.inlet = StreamInlet(streams[0], max_buflen=1) # max_buflen=1 for real time (samples will be dropped instead instead of buffered)
        print('found')



    def pull_sample(self):
        """returns inlet.pull_sample()"""
        return self.inlet.pull_sample()