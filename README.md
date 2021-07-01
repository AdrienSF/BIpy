# BIpy package

Python package to help build experiments at the Brain Institute. It’s main purpose is to help using the real-time BCI.
<!-- examples, basic usage -->

## Module contents

BCI:<br>
bci.classifier_process.run_classifier<br>
bci.classifier_process.ClassifierProcess

bci.inlets.WindowInlet<br>
bci.inlets.ClassifierInlet

bci.models.DummyClassifier<br>
bci.models.get_trained_CSP_LDA

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


## Submodules

## BIpy.data_processing module


### class BIpy.data_processing.LowpassWrapper(lowcut=70, sf=500, order=6, axis=2)
Bases: `sklearn.base.TransformerMixin`

Wrapper class for using lowpass_filter in an sklearn pipeline

fit_transform(data)

> Low pass filters data

transform(data) = fit_transform

> Also low pass filters data


#### \__init__(lowcut=70, sf=500, order=6, axis=2)
lowcut

> Upper limit in hz, above which frequencies are filtered out.<br>
> Default 70

sf

> Sampling frequency, defualt 500

order

> Passed to scipy.signal.butter, default 6

axis

> Axis along which the filter is performed, with axis=2 it can filter the entire data cube at once<br>
> Default 2, and default should always be used with input data shape (trials, channels, time)


### BIpy.data_processing.get_sliding_window_partition(data, labels, window_size)
Splits data into several windows

data

> EEG data with shape (trials, channels, time)

labels

> 1d array of integer labels corresponding to left/right

window_size

> Size in samples (not time) of the windows the data will be split into<br>
> If window_size corresponds to the number of recorded samples per trial, the function returns the input data and labels unchaged

windowed_data

> Array of shape (windows, channels, time)

windowed_labels

> 1d array of labels corresponding to each window


### BIpy.data_processing.lowpass_filter(data, lowcut=70, sf=500, order=6, axis=2)
Low pass filter

data

> Shape (trials, channels, time)

lowcut

> Upper limit in hz, above which frequencies are filtered out.<br>
> Default 70

sf

> Sampling frequency, defualt 500

order

> Passed to scipy.signal.butter, default 6

axis

> Axis along which the filter is performed, with axis=2 it can filter the entire data cube at once<br>
> Default 2, and default should always be used with input data shape (trials, channels, time)

y

> Filtered data, of same shape as input


### BIpy.data_processing.organize_xdf(xdf_filename, trial_duration, gelled_indeces=[5, 6, 7, 10, 11, 21, 22, 24, 27, 28, 38, 39, 40, 42, 53, 55, 56, 57], stim_channel=67, instructed_trigger_map={'instructed_left': 12, 'instructed_right': 13})
Function to organize motor imagery xdf data into labeled epochs. Does not support free trials

Free tip: avoid using xdf data wherever possible

xdf_filename

> The file location of the xdf data to load and organize

trial_duration

> The duration in seconds of each motor imagery trial

gelled_indeces

> The indices of relevant electrodes, the data from all other electrodes will be discarded.<br>
> By default fc_c_cp_1through6, the indeces corresponding to electrodes fc, c, and cp 1 through 6, found to be most useful for BCI<br>
> Index <=> electrode mappings can be found in BIpy.electrode_info.csv

stim_channel

> The channel used for triggers/events, by default 67

instructed_trigger_map

> Trigger/event values for instructed left/right motor imagery trials, with keys instructed_left, instructed_right<br>
> and int or list of int values

organized_data

> Numpy array of shape (trials, channels, time) containing extracted epochs

labels

> Numpy array of shape (trials,) where labels[trial_num] corresponds to organized_data[trial_num]<br>
> The labels are integers corresponing to instructed_trigger_map[instructed_left] and instructed_trigger_map[instructed_right]

## BIpy.session module


### class BIpy.session.Session(info, blocks, use_json=False)
Bases: `object`

A class that handles the execution and data collection of a Psychopy experiment

info

> Information about the session, ex: {‘session_id’: 1234}

blocks

> List of blocks, each block a list of trials, each trial a function that takes exactly one input: ‘logger’<br>
> each trial function should execute the intended trial

use_json

> Flag to indicate whether or not to save data to json on calling save()

to_hide

> List of trials to be ignored when saving to csv

log_history

> Used to store trial data on call of log()

_iq

> Index queue, list of tuples corresponding to the indeces of each trial function in blocks

run

> Iterates through and runs all trial functions of blocks in order

log(to_log: dict, save_to_file=True)

> Stores to_log in log_history[current_block_num][current_trial_num]

hide_trial

> Marks current trial to be ignored when saving to csv

save

> Attempts to find an apropriate filename, and calls save_to_csv(filename)<br>
> if use_json is True, also calls save_to_json(filename)

save_to_csv(filename)

> Saves the Session’s info, and log_history to filename in csv format

get_current

> Returns the current block and trial nuber: tuple (block, trial)

save_to_json(filename)

> Saves as much information about the current Session object as possible to filename in json format


#### \__init__(info, blocks, use_json=False)
info

> Information about the session, ex: {‘session_id’: 1234}

blocks

> List of blocks, each block a list of trials, each trial a function that takes exactly one input: ‘logger’<br>
> each trial function should execute the intended trial

use_json

> Flag to indicate whether or not to save data to json on calling save()


#### get_current()
Returns the current block and trial nuber


#### hide_trial()
Marks current trial to be ignored when saving to csv


#### log(to_log, save_to_file=True)
Stores to_log in log_history[current_block_num][current_trial_num]

to_log: dict

> Python dict with information to save from the current trial, ex: {‘RT’: .129486}

save_to_file: bool, defaul=True

> Flag to save data to file<br>
> this can take time so set to False if you want to log some data but the current trial needs strict timing,<br>
> then call Session.save() a the end of the experiment


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
