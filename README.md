# BIpy package

## Submodules

## BIpy.data_processing module


### class BIpy.data_processing.LowpassWrapper(lowcut=70, sf=500, order=6, axis=2)
Bases: `sklearn.base.TransformerMixin`

Wrapper class for using lowpass_filter in an sklearn pipeline

> fit_transform(data)

Low pass filters data

    transform(data) = fit_transform

Also low pass filters data


#### \__init__(lowcut=70, sf=500, order=6, axis=2)
lowcut

    Upper limit in hz, above which frequencies are filtered out.
    Default 70

sf

    Sampling frequency, defualt 500

order

    Passed to scipy.signal.butter, default 6

axis

    Axis along which the filter is performed, with axis=2 it can filter the entire data cube at once
    Default 2, and default should always be used with input data shape (trials, channels, time)


### BIpy.data_processing.get_sliding_window_partition(data, labels, window_size)
Splits data into several windows

data

    EEG data with shape (trials, channels, time)

labels

    1d array of integer labels corresponding to left/right

window_size

    Size in samples (not time) of the windows the data will be split into
    If window_size corresponds to the number of recorded samples per trial, the function returns the input data and labels unchaged

windowed_data

    Array of shape (windows, channels, time)

windowed_labels

    1d array of labels corresponding to each window


### BIpy.data_processing.lowpass_filter(data, lowcut=70, sf=500, order=6, axis=2)
Low pass filter

data

    Shape (trials, channels, time)

lowcut

    Upper limit in hz, above which frequencies are filtered out.
    Default 70

sf

    Sampling frequency, defualt 500

order

    Passed to scipy.signal.butter, default 6

axis

    Axis along which the filter is performed, with axis=2 it can filter the entire data cube at once
    Default 2, and default should always be used with input data shape (trials, channels, time)

y

    Filtered data, of same shape as input


### BIpy.data_processing.organize_xdf(xdf_filename, trial_duration, gelled_indeces=[5, 6, 7, 10, 11, 21, 22, 24, 27, 28, 38, 39, 40, 42, 53, 55, 56, 57], stim_channel=67, instructed_trigger_map={'instructed_left': 12, 'instructed_right': 13})
Function to organize motor imagery xdf data into labeled epochs. Does not support free trials

Free tip: avoid using xdf data wherever possible

xdf_filename

    The file location of the xdf data to load and organize

trial_duration

    The duration in seconds of each motor imagery trial

gelled_indeces

    The indices of relevant electrodes, the data from all other electrodes will be discarded.
    By default fc_c_cp_1through6, the indeces corresponding to electrodes fc, c, and cp 1 through 6, found to be most useful for BCI
    Index <=> electrode mappings can be found in BIpy.electrode_info.csv

stim_channel

    The channel used for triggers/events, by default 67

instructed_trigger_map

    Trigger/event values for instructed left/right motor imagery trials, with keys instructed_left, instructed_right
    and int or list of int values

organized_data

    Numpy array of shape (trials, channels, time) containing extracted epochs

labels

    Numpy array of shape (trials,) where labels[trial_num] corresponds to organized_data[trial_num]
    The labels are integers corresponing to instructed_trigger_map[instructed_left] and instructed_trigger_map[instructed_right]

## Module contents

Python package to help build experiments at the Brain Institute. Currently it’s use is to help using the BCI.

Data Processing:
data_processing.default_instructed_trigmap
data_processing.default_free_trigmap
data_processing.fc_c_cp_1through6
data_processing.organize_xdf
data_processing.get_sliding_window_partition
data_processing.lowpass_filter
data_processing.LowpassWrapper

BCI:
bci.classifier_process.run_classifier
bci.classifier_process.ClassifierProcess

bci.inlets.WindowInlet
bci.inlets.ClassifierInlet

bci.models.DummyClassifier
bci.models.get_trained_CSP_LDA

Other:
electrode_info.csv
electrode_info.json
