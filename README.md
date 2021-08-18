# BIpy package

Python package to help build experiments at the Brain Institute. It’s main purpose is to help using the real-time BCI.


## Module contents

BCI:<br>
bci.classifier_process.run_classifier<br>
bci.classifier_process.ClassifierProcess

bci.inlets.WindowInlet<br>
bci.inlets.ClassifierInlet

bci.models.DummyClassifier<br>
bci.models.get_trained_CSP_LDA

bci.stims.NeuroFeedbackStim

bci.training_session.TraininSession

Data Processing:<br>
data_processing.default_instructed_trigmap<br>
data_processing.default_free_trigmap<br>
data_processing.fc_c_cp_1through6<br>
data_processing.organize_xdf<br>
data_processing.get_sliding_window_partition<br>
data_processing.lowpass_filter<br>
data_processing.LowpassWrapper

Session:<br>
session.Session

Other:<br>
electrode_info.csv<br>
electrode_info.json


### Example usage of Session
```python
    from BIpy.sesssion import Session
    import random
    import numpy as np

    # [OMITTED]: Psychopy stuff such as making window, stims...

    def instructions(logger):
        # display some instructions
        text_stim.draw()
        win.flip()
        event.waitKeys()
        # hide this trial so it doesn't show up in the saved csv file
        logger.hide_trial()

    def discrimination_RT_trial(logger):
        # wait for keypress to start trial
        event.waitKeys()

        # present fixation cross (random amount of time)
        cross.draw()
        win.flip()
        core.wait(random.uniform(1,2))

        # present l/r arrow at random
        is_left = random.choice([0,1])
        if is_left:
            left_arrow.draw()
        else:
            right_arrow.draw()

        # get reaction time
        win.flip()
        key_pressed, RT = event.waitKeys(keyList=['0', '1'], timeStamped=core.Clock())[0]

        # log key pressed, RT, and which arrow was displayed to a csv file
        info = {'RT': RT, 'key_pressed': key_pressed, 'is_left': is_left}
        logger.log(info)

        # get current block and trial number
        current_block_num, current_trial_num = logger.get_current()
        # get all past trials this block
        past_trials = logger.log_history[current_block_num][:current_trial_num]
        # get average past correct reaction time for the current block
        mean_rt = np.mean([ trial['rt'] for trial past_trials if str(trial['is_left']) == trial['key_pressed'] ])

        # display feedback to the participant
        if str(is_left) != key_pressed:
            text_stim.text = 'Wrong side!'
        elif RT > mean_rt:
            text_stim.text = 'Slower than average'
        else:
            text_stim.text = 'Faster than average'

        text_stim.draw()
        win.flip()
        core.wait(1)




    # set up trials and blocks
    # first block will just be instructions 
    instruction_block = [instructions]
    # second block will be 4 discrimination RT trials
    trial_block = [discrimination_RT_trial, discrimination_RT_trial, discrimination_RT_trial, discrimination_RT_trial]
    blocks = [instruction_block, trial_block]

    # some info about the experiment we might want saved
    refresh_rate = win.monitorFramePeriod
    sess_id = input('Enter session id:')
    info = {'sess_id': sess_id, 'refresh_rate': refresh_rate}

    session = Session(info, blocks)
    session.run()

    # exit Psychopy
    win.close()
    core.quit()
```

### Example usage of BCI
```python
    import BYpy.bci as bci
    import numpy as np
    from Psychopy import event, core, visual
    from pylsl import resolve_stream, StreamInlet
    # do Psychopy stuff
    win = visual.Window(monitor='testMonitor', fullscr=True)
    text_stim = visual.TextStim(win, color='grey')


    # train classifier on previously recorded data
    data = np.load('some_data.npy')
    labels = np.load('some_labels.npy')

    clf = bci.models.get_trained_CSP_LDA(data, labels)

    # start a classifier process that runs in the background, 
    # in_source_id='myuid323457' corresponds to the stream of data from dry eeg that will be classified via CSP + LDA
    # window_size=500 means the classifier will use the past 500 samples from the dry eeg as input
    clfproc = bci.classifier_process.ClassifierProcess(clf, in_source_id='myuid323457', out_source_id='classifier_output', window_size=500)

    # listen to the output of the classifier
    inlet = bci.inlets.ClassifierInlet(source_id='classifier_output')

    for _ in range(100):
        # get a new sample from the classifer every second for 100 seconds
        core.wait(1)
        sample, timestamp = inlet.pull_sample()

        # display the classifier's prediction on screen
        text_stim.text = str(sample)
        text_stim.draw()
        win.flip()

    
    # stop the classifier process, if not it could keep running in the background indefinetly
    clfproc.kill()
    clfproc.join()
    clfproc.close()

    # exit Psychopy
    win.close()
    core.quit()
```

### Example usage of TrainingSession
```python
    from training_session import TrainingSession
    from psychopy import visual, core

    win = visual.Window(monitor='testMonitor', fullscr=True)

    sess = TrainingSession(win, iterations=5, trials_per_iteration=20)

    sess.run()
    win.close()
    core.quit()
```



## Submodules

## BIpy.data_processing module


### class BIpy.data_processing.LowpassWrapper(lowcut=70, sf=500, order=6, axis=2)
Bases: `sklearn.base.TransformerMixin`

Wrapper class for using lowpass_filter in an sklearn pipeline

fit_transform(data)

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


### BIpy.data_processing.get_sliding_window_partition(data, labels, window_size, step=1)
Splits data into several windows. Deprecated (waste of memory)

data

    EEG data with shape (trials, channels, time)

labels

    1d array of integer labels corresponding to left/right

window_size

    Size in samples (not time) of the windows the data will be split into
    If window_size corresponds to the number of recorded samples per trial, the function returns the input data and labels unchaged

step

    Step size of the sliding window

windowed_data

    Array of shape (windows, channels, time)

windowed_labels

    1d array of labels corresponding to each window


### BIpy.data_processing.get_windows(data, labels, window_size, step_size)
Splits data into several windows

data

    EEG data with shape (trials, channels, time)

labels

    1d array of integer labels corresponding to left/right

window_size

    Size in samples (not time) of the windows the data will be split into
    If window_size corresponds to the number of recorded samples per trial, the function returns the input data and labels unchaged

step

    Step size of the sliding window

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


### BIpy.data_processing.sliding_window_iter(total_size, window_size)
Helper function to get a sliding window view of indexes

## BIpy.session module


### class BIpy.session.Session(info, blocks, use_json=False, hide_info=False, suppress_save=False)
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


#### \__init__(info, blocks, use_json=False, hide_info=False, suppress_save=False)
info

    Information about the session, ex: {‘session_id’: 1234}

blocks

    List of blocks, each block a list of trials, each trial a function that takes exactly one input: ‘logger’
    each trial function should execute the intended trial

use_json

    Flag to indicate whether or not to save data to json on calling save()

suppress_save

    Flag to indicate log() calls should never save to file save to file

hide_info

    Flag to indicate if ‘info’ should be saved to csv


#### get_current()
Returns the current block and trial nuber: tuple (block, trial)


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


## BIpy.bci.classifier_process module


### BIpy.bci.classifier_process.ClassifierProcess(clf, in_source_id='myuid323457', out_source_id='classifier_output', stream_no=0, window_size=500)
Returns a multiprocessing.process of run_classifier

clf

    Classifier to run

in_source_id

    Pylsl stream source_id of incoming data to be fed to the classifier

        Default myuid323457 - dry EEG, for ActiChamp use 17010768

out_source_id

    Pylsl stream source_id for output of the classifier
    Default ‘classifier_output’

strem_no

    Index of the stream. Should be 0 or 1, ask Tian for help on this
    Default 0

window_size

    Number of samples required as input to the provided classifier clf
    If None, the function will attenpt to get this from clf.window_size
    Default None

multiprocessing.process() of BIpy.classifier_process.run_classifier()


### BIpy.bci.classifier_process.run_classifier(clf, in_source_id='myuid323457', out_source_id='classifier_output', stream_no=0, window_size=None)
Runs a real-time classifier untill killed

clf

    Classifier to run. Must be able to take the output of WindowInlet.pull_window() as input to clf.predict_proba(), 
    and clf.predict_proba(data) must output a single float

in_source_id

    Pylsl stream source_id of incoming data to be fed to the classifier

        Default myuid323457 - dry EEG, for ActiChamp use 17010768

out_source_id

    Pylsl stream source_id for output of the classifier

strem_no

    Index of the stream. Should be 0 or 1, ask Tian for help on this
    Default 0

window_size

    Number of samples required as input to the provided classifier clf
    If None, the function will attenpt to get this from clf.window_size

For every input recieved, immediately pushes the provided classifiers output (predict_proba(data)) to lsl

## BIpy.bci.inlets module


### class BIpy.bci.inlets.ClassifierInlet(source_id='classifier_output')
Bases: `object`

A class used like a pylsl inlet, but made for getting the output of a real-time classifier

inlet

    Pylsl inlet from which the output of a classifier is pulled

pull_sample

    returns inlet.pull_sample()


#### \__init__(source_id='classifier_output')
source_id

    Pylsl stream source_id for incoming data
    Default ‘classifier_output’


#### pull_sample()
returns inlet.pull_sample()


### class BIpy.bci.inlets.WindowInlet(source_id='myuid323457', stream_no=0, window_size=500)
Bases: `object`

A class used like a pylsl inlet, but that returns window_size past samples on each pull_window
Attributes
———-
inlet : pylsl.StreamInlet

> Pylsl inlet from which real-time EEG data is pulled

window_size

    Width in samples (not seconds) of the sliding window

window

    List of window_size last samples pulled from inlet

pull_window

    Pulls the last window_size from inlet


#### \__init__(source_id='myuid323457', stream_no=0, window_size=500)
> source_id

>     Pylsl stream source_id of incoming data buffered for sliding window
>     Default myuid323457 - dry EEG, for ActiChamp use 17010768

> stream_no

>     Index of the stream. Should be 0 or 1, ask Tian for help on this
>     Default 0

> window_size

>     Number of past samples returned on call of pull_window
>     Default 500

> transpose_output

>     If True transposes the output of the window so that it has the shape expected by mne’s CSP


#### pull_window(window_size=None, timeout=0.25)
Pulls the last window_size samples from inlet

window_size

    Width in samples (not seconds) of the sliding window
    If None, uses self.window_siz, Default None

timeout

    Timeout in seconds passed to pylsl.inlet.pull_chunk
    Default .25

window

    list of window_size last samples pulled from inlet

## BIpy.bci.models module


### class BIpy.bci.models.DummyClassifier()
Bases: `object`

Dummy classifier for testing purpose


#### \__init__()

#### predict_proba(data)
returns input[0]


### class BIpy.bci.models.WrappedCSPLDAClassifier(data_channels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], window_size=1000, preprocessing=<BIpy.data_processing.LowpassWrapper object>)
Bases: `object`

Wrapper class for using an sklearn csp+lda pipeline in a BIpy.bci.ClassifierProcess

predict_proba(self, window: np.array)

    takes the output form a WindowInlet and returns the probability (according to the csp+lda classifier) that the right hand was imagined

def fit(self, data, labels):

    calls fit(data, labels) on the csp+lda classifier


#### \__init__(data_channels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], window_size=1000, preprocessing=<BIpy.data_processing.LowpassWrapper object>)
data_channels

    Channels that the classifier should use as input

window_size

    number of samples of eeg data the classifier should use as input

preprocessing

    Step added to the start of the csp+lda sklearn pipeline


#### fit(data, labels)
calls fit(data, labels) on the csp+lda classifier


#### predict_proba(window)
takes the output form a WindowInlet and returns the probability (according to the csp+lda classifier) that the right hand was imagined


### BIpy.bci.models.get_trained_CSP_LDA(data, labels, window_size=None, preprocessing=<BIpy.data_processing.LowpassWrapper object>, step_size=None)
Returns a trained sklearn pipeline of [csp, lda]

data

    Data to train the classifier on
    Shape (trials, channels, time)

labels

    1d array of labels to the training data

window_size

    Size in samples (not seconds) the classifier should be trained on
    If None, the function will trian with each entire trial as input
    Default None

preprocessing

    Preprocessing step to add at the beggining of the sklearn pipeline
    Default BIpy.preprocessing.LowpassWraspper()

step_size

    Stride/step size passed to BIpy.data_processing.get_windows()
    If None, classifier will be trained on raw data and get_windows() is never used

clf

    A trained csp + lda Pipeline

## BIpy.bci.stims module


### class BIpy.bci.stims.NeuroFeedbackStim(win, resolution)
Bases: `object`

Progress bar style stim for displaying classifier output to the subject

draw(self, porportion=None)

    draws the stim


#### \__init__(win, resolution)
win

    window in which the stim will be drawn

resolution

    number of segments in on each side of the “progress bar”


#### draw(proportion=None)
draws the stim

proportion

    value between 0 and 1. At 0 the “progress bar” reaches all the way to the left, and at 1 it reaches the right

## BIpy.bci.training_session module


### BIpy.bci.training_session.TrainingSession(win, iterations, trials_per_iteration, clf=<BIpy.bci.models.WrappedCSPLDAClassifier object>, trial_duration=4, sampling_rate=500, data_channels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], window_size=500, step_size=100, eeg_source_id='myuid323457', eeg_stream_no=0, resolution=6)
Returns a Session object that runs an iterative training session.

The returned Session performs a block of neurofeedback trials, then re-trains the classifier on the newly collected data and runs a new block of neurofeedback trials. The EEG data, classifier predictions and true labels are saved to files. The defaults of this function are suitable for dry EEG

win

    window in which the session will occur

iterations

    number of blocks/ number of times the classifier is re-trained on new data

trials_per_iteration

    number of trials per block

clf

    the classifier used to predict left/right motor imagery

trial_duration

    duration in seconds of each trial

sampling_rate

    sampling rate of data sent to the EEG lsl stream

data_channels

    indeces of the electrode channels the classifier should use as input

window_size: int, default 500

    number of samples the given classifier should take as input at once

step_size

    the given classifier is trained on multiple windows spanning the data collected in one trial. step_size is the gap (in samples) between the start of each window.
    if one trial contains 800 samples of eeg data, the window size is 400 and the step size is 200, then the classifier will be trained using 3 windows for each trial: samples 0-400, 200-600, and 400-800
    the window size, step size and samples per trial need not line up perfectly, all data will be used for training regardless (but the last step size will differ from the rest)

eeg_source_id

    Pylsl stream source_id of incoming eeg data to be fed to the classifier
    Default myuid323457 - dry EEG, for ActiChamp use 17010768

eeg_stream_no

    Index of the stream. Should be 0 or 1, ask Tian for help on this

resolution

    number of segments in on each side of the BIpy.bci.stims.NeuroFeedbackStim displayed on screen

