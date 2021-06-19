# BIpy package

Python package to help build experiments at the Brain Institute. It’s main purpose is to help using the real-time BCI.
<!-- examples, basic usage -->

## Module contents

BCI:
bci.classifier_process.run_classifier
bci.classifier_process.ClassifierProcess

bci.inlets.WindowInlet
bci.inlets.ClassifierInlet

bci.models.DummyClassifier
bci.models.get_trained_CSP_LDA

Data Processing:
data_processing.default_instructed_trigmap
data_processing.default_free_trigmap
data_processing.fc_c_cp_1through6
data_processing.organize_xdf
data_processing.get_sliding_window_partition
data_processing.lowpass_filter
data_processing.LowpassWrapper

Session:
session.Session

Other:
electrode_info.csv
electrode_info.json

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

## BIpy.session module


### class BIpy.session.Session(info, blocks, use_json=False)
Bases: `object`

A class that handles the execution and data collection of a Psychopy experiment

info

    Information about the session, ex: {‘session_id’: 1234}

blocks

    List of blocks, each block a list of trials, each trial a function that takes exactly one input: ‘logger’
    each trial function should execute the intended trial

use_json

    Flag to indicate whether or not to save data to json on calling save()

to_hide

    List of trials to be ignored when saving to csv

log_history

    Used to store trial data on call of log()

_iq

    Index queue, list of tuples corresponding to the indeces of each trial function in blocks

run

    Iterates through and runs all trial functions of blocks in order

log(to_log: dict, save_to_file=True)

    Stores to_log in log_history[current_block_num][current_trial_num]

hide_trial

    Marks current trial to be ignored when saving to csv

save

    Attempts to find an apropriate filename, and calls save_to_csv(filename)
    if use_json is True, also calls save_to_json(filename)

save_to_csv(filename)

    Saves the Session’s info, and log_history to filename in csv format

get_current

    Returns the current block and trial nuber

save_to_json(filename)

    Saves as much information about the current Session object as possible to filename in json format


#### \__init__(info, blocks, use_json=False)
info

    Information about the session, ex: {‘session_id’: 1234}

blocks

    List of blocks, each block a list of trials, each trial a function that takes exactly one input: ‘logger’
    each trial function should execute the intended trial

use_json

    Flag to indicate whether or not to save data to json on calling save()


#### get_current()
Returns the current block and trial nuber


#### hide_trial()
Marks current trial to be ignored when saving to csv


#### log(to_log, save_to_file=True)
Stores to_log in log_history[current_block_num][current_trial_num]

to_log: dict

    Python dict with information to save from the current trial, ex: {‘RT’: .129486}

save_to_file: bool, defaul=True

    Flag to save data to file
    this can take time so set to False if you want to log some data but the current trial needs strict timing,
    then call Session.save() a the end of the experiment


#### run()
Iterates through and runs all trial functions of blocks in order


#### save()
Attempts to find an apropriate filename, and calls save_to_csv(filename)

If self.use_json is True, also calls save_to_json(filename)


#### save_to_csv(filename)
Saves the Session’s info, and log_history to filename in csv format

filename : str


#### save_to_json(filename)
Saves as much information about the current Session object as possible to filename in json format

filename : str


### BIpy.session.is_jsonable(x)
