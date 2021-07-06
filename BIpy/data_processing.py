from  numpy.lib.stride_tricks import sliding_window_view
from scipy import signal as sg
import numpy as np
import mne
import pyxdf
from sklearn.base import TransformerMixin

from itertools import islice
from collections import deque


default_instructed_trigmap = {
    'instructed_left': 12,
    'instructed_right': 13
}
# default_instructed_trigmap.__doc__ = 'Default trigger/event values in gel EEG data for instructed left/right motor imagery trials'

default_free_trigmap = {
    'free_start': 14,
    'free_left': 15,
    'free_right': 16
}
# default_free_trigmap.__doc__ = 'Default trigger/event values in gel EEG data for free choice left/right motor imagery trials'








# for gell EEG use electrodes fc, c, and cp 1 through 6 corresponding to indeces:
fc_c_cp_1through6 = [5, 6, 7, 10, 11, 21, 22, 24, 27, 28, 38, 39, 40, 42, 53, 55, 56, 57]
# fc_c_cp_1through6.__doc__ = 'Indeces corresponding to electrodes fc, c, and cp 1 through 6, found to be most useful for BCI. Index <=> electrode mappings can be found in BIpy.electrode_info.csv'

# (for some of my data it seems only electrodes > 32 were gelled, leaving: 
# [38, 39, 40, 42, 53, 55, 56, 57]

def organize_xdf(xdf_filename: str, trial_duration: float, gelled_indeces=fc_c_cp_1through6, stim_channel=67, instructed_trigger_map=default_instructed_trigmap):
    """Function to organize motor imagery xdf data into labeled epochs. Does not support free trials

    Free tip: avoid using xdf data wherever possible

    Parameters
    ----------
    xdf_filename : str
        The file location of the xdf data to load and organize
    trial_duration : float
        The duration in seconds of each motor imagery trial
    gelled_indeces : list, optional
        The indices of relevant electrodes, the data from all other electrodes will be discarded.
        By default fc_c_cp_1through6, the indeces corresponding to electrodes fc, c, and cp 1 through 6, found to be most useful for BCI
        Index <=> electrode mappings can be found in BIpy.electrode_info.csv
    stim_channel : int
        The channel used for triggers/events, by default 67
    instructed_trigger_map : dict
        Trigger/event values for instructed left/right motor imagery trials, with keys instructed_left, instructed_right
        and int or list of int values

    Returns
    -------
    organized_data : np.array
        Numpy array of shape (trials, channels, time) containing extracted epochs
    labels : np.array
        Numpy array of shape (trials,) where labels[trial_num] corresponds to organized_data[trial_num]
        The labels are integers corresponing to instructed_trigger_map[instructed_left] and instructed_trigger_map[instructed_right]
    """
    
    
    streams, header = pyxdf.load_xdf("data.xdf")
    data = streams[0]["time_series"].T

    total_channels = data.shape[0]

    assert total_channels >= max(gelled_indeces) + 2
    if total_channels != 68:
        raise Warning('Expected 68 channels but found: ' + str(total_channels))

    # data = data[gelled_indeces]
    # total_gelled = data.shape[0]
    sfreq = float(streams[0]["info"]["nominal_srate"][0])
    info = mne.create_info(total_channels, sfreq=sfreq)
    raw = mne.io.RawArray(data, info)

    events = mne.find_events(raw, stim_channel = str(stim_channel))

    trials = []
    labels = []
    for trig_name in instructed_trigger_map:
        if type(instructed_trigger_map[trig_name]) == list or type(instructed_trigger_map[trig_name]) == tuple:
            event_id = instructed_trigger_map[trig_name]
            label = instructed_trigger_map[trig_name][0]
        else:
            event_id = [instructed_trigger_map[trig_name]]
            label = instructed_trigger_map[trig_name]
        
        epochs = mne.Epochs(raw, events, event_id=event_id, tmin=0, tmax=trial_duration, baseline=(0,0)).get_data()


        # transpose each epoch to get samples as rows and channels as columns -- NOT because mne's CSP expects transpose
        for trial_num in range(epochs.shape[0]):
            # keep only gelled channels
            trials.append(epochs[trial_num, gelled_indeces])#.T)
            labels.append(label)
        

    # turn list of trials into numpy array
    organized_data = np.stack(trials, axis=0)

    return organized_data, np.array(labels)





# sliding window over time for data.shape = (trial, channel, time)
def get_sliding_window_partition(data, labels, window_size, step=1):
    """Splits data into several windows. Deprecated (waste of memory)

    Parameters
    ----------
    data : np.array
        EEG data with shape (trials, channels, time)
    labels : np.array
        1d array of integer labels corresponding to left/right
    window_size : int
        Size in samples (not time) of the windows the data will be split into
        If window_size corresponds to the number of recorded samples per trial, the function returns the input data and labels unchaged
    step : int, default 1
        Step size of the sliding window

    Returns
    -------
    windowed_data : np.array
        Array of shape (windows, channels, time)
    windowed_labels : np.array
        1d array of labels corresponding to each window
    """

    raise DeprecationWarning('This function uses way too much memory')

    assert len(data.shape) == 3
    if data.shape[2] == window_size:
        return data, labels

    windowed_data = np.empty((0, data.shape[1], window_size))
    windowed_labels = np.empty((0,))
    for i in range(data.shape[0]):
        trial = data[i]
        # print(trial)
        windows = sliding_window_view(trial, (data.shape[1], window_size))[0]
        # print('windows')
        # print(windows)
        windowed_data = np.append(windowed_data, windows, axis=0)


        new_labels = np.array([ labels[i] for _ in range(windows.shape[0]) ])
        # print('labels')
        # print(new_labels)
        windowed_labels = np.append(windowed_labels, new_labels, axis=0)


    return windowed_data[::step], windowed_labels[::step]

def sliding_window_iter(total_size, window_size):
    """Helper function to get a sliding window view of indexes"""
    iterable = iter(range(total_size))
    window = deque(islice(iterable, window_size), maxlen=window_size)
    for item in iterable:
        yield list(window)
        window.append(item)
    if window:  
        # needed because if iterable was already empty before the `for`,
        # then the window would be yielded twice.
        yield list(window)

def get_windows(data, labels, window_size: int, step_size: int):
    """Splits data into several windows

    Parameters
    ----------
    data : np.array
        EEG data with shape (trials, channels, time)
    labels : np.array
        1d array of integer labels corresponding to left/right
    window_size : int
        Size in samples (not time) of the windows the data will be split into
        If window_size corresponds to the number of recorded samples per trial, the function returns the input data and labels unchaged
    step : int
        Step size of the sliding window

    Returns
    -------
    windowed_data : np.array
        Array of shape (windows, channels, time)
    windowed_labels : np.array
        1d array of labels corresponding to each window
    """

    indeces_list = np.array(list(sliding_window_iter(data.shape[-1], window_size)))[::step_size]
    return np.array([data[:,:,indeces] for indeces in indeces_list]), np.array(list(labels)*data.shape[0])

# low pass 70hz
# data.shape = (trials, channels, time)  -- with axis=2 it can filter the entire data cube at once
def lowpass_filter(data, lowcut=70 , sf=500, order=6, axis=2):
    """Low pass filter

    Parameters
    ----------
    data : np.array
        Shape (trials, channels, time)
    lowcut : int
        Upper limit in hz, above which frequencies are filtered out.
        Default 70
    sf : int
        Sampling frequency, defualt 500
    order : int
        Passed to scipy.signal.butter, default 6
    axis : int
        Axis along which the filter is performed, with axis=2 it can filter the entire data cube at once
        Default 2, and default should always be used with input data shape (trials, channels, time)

    Returns
    -------
    y : np.array
        Filtered data, of same shape as input
    """


    nyq = 0.5 * sf
    low = lowcut / nyq
    b, a = sg.butter(order, low, btype='low', analog=False)
    y = sg.lfilter(b, a, data, axis=axis)
    return y


class LowpassWrapper(TransformerMixin):
    """Wrapper class for using lowpass_filter in an sklearn pipeline

    Methods
    -------
    fit_transform(data)
        Low pass filters data
    transform(data) = fit_transform
        Also low pass filters data
    """



    def __init__(self, lowcut=70 ,sf=500, order=6, axis=2):
        """
            Parameters
            ----------
            lowcut : int
                Upper limit in hz, above which frequencies are filtered out.
                Default 70
            sf : int
                Sampling frequency, defualt 500
            order : int
                Passed to scipy.signal.butter, default 6
            axis : int
                Axis along which the filter is performed, with axis=2 it can filter the entire data cube at once
                Default 2, and default should always be used with input data shape (trials, channels, time)

        """

        self.fit_transform = lambda data, x=None : lowpass_filter(data, lowcut, sf, order, axis)
        self.transform = self.fit_transform


    def __str__(self):
        return 'low_pass_filter'