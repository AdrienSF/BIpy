import numpy as np
import random
import gc

from BIpy.session import Session
from BIpy.data_processing import get_sliding_window_partition
from stims import NeuroFeedbackStim
from classifier_process import ClassifierProcess
from inlets import ClassifierInlet
from models import WrappedCSPLDAClassifier

from psychopy import visual, core, event
from pylsl import StreamInlet, resolve_stream

# ####
from BIpy.data_processing import LowpassWrapper
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import Pipeline
from mne.decoding import CSP
# ####

win = visual.Window(monitor='testMonitor', fullscr=True)
text_stim = visual.TextStim(win)
nf_stim = NeuroFeedbackStim(win, 6)

def collect(logger):
    print('starting collect trial')
    info = logger.info

    # ask to start
    text_stim.text = 'Press any key to start.'
    text_stim.draw()
    win.flip()
    event.waitKeys()
    win.flip()
    # 2 sec delay
    core.wait(2)
    # loop for 4 seconds neurofeedback, start recording eeg data
    trial_data = []
    predict_probas = []
    clock = core.Clock()
    print('starting main loop')
    # wait until classifier process is ready to start classifying
    info['cinlet'].pull_sample()
    # clear eeg lsl buffer
    info['eeg_inlet'].pull_chunk(max_samples=int(1e6))
    while clock.getTime() < info['trial_duration'] or len(trial_data) < 2000: # [NOTE] keep going if there happen to not be enough samples. un-hard-code this
        # neurofeedback
        prob = info['cinlet'].pull_sample()[0][0] # sample = [[prob], timestamp]
        # print('pulled sample:', prob)
        nf_stim.draw(prob)
        win.flip()
        trial_data = trial_data + info['eeg_inlet'].pull_chunk()[0]
        predict_probas.append(prob)

# do one more iteration of neurofeedback, since it seems I'm not getting 2000 samples total [NOTE]
    # neurofeedback
    # prob = info['cinlet'].pull_sample()[0][0] # sample = [[prob], timestamp]
    # # print('pulled sample:', prob)
    # nf_stim.draw(prob)
    # win.flip()
    # trial_data = trial_data + info['eeg_inlet'].pull_chunk()[0]
    # predict_probas.append(prob)


    # ask for label
    text_stim.text = 'Which side were you imagining? press 1 for left and 0 for right'
    text_stim.draw()
    win.flip()
    key = event.waitKeys(keyList=['0', '1'])
    label = int('0' in key)

    # append label and data to info
    # change trial data to mne's CSP input format
    print('untrimmed trial_data shape:', np.array(trial_data).shape)

    trial_data = np.transpose(np.array(trial_data)[:2000,:20]) # [NOTE]: first 2000 samples, first 20 channels
    print('trial_data shape:', trial_data.shape)
    info['data'] = np.vstack((info['data'], [trial_data]))
    info['labels'].append(label)
    print('[collect]: data shape:', np.array(info['data']).shape)
    # log true label and list of predict proba?
    logger.log({'label': label, 'predict_probas': predict_probas})

def train(logger):
    logger.hide_trial()
    info = logger.info
    # kill old classifier (if there is one)
    if 'cproc' in info and info['cproc']:
        info['cproc'].kill()
        info['cproc'].join()
        info['cproc'].close()
    # split data into the right size chunks for clf input # [NOTE] do something about this ridiculous reshape
    print('[train]: data shape:', np.array(info['data']).shape)
    gc.collect()
    data, labels = get_sliding_window_partition(info['data'], np.array(info['labels']), window_size=info['window_size'], step=200)
    print('windowed data shape:', data.shape)
    # re-train model
    info['clf'].fit(data, labels)
    # re-start classifier process
    info['cproc'] = ClassifierProcess(info['clf'], info['eeg_source_id'], window_size=info['window_size'], stream_no=info['eeg_stream_no'])
    info['cproc'].start()

    # make new classifier inlet in case the previos timed out
    info['cinlet'] = ClassifierInlet()
    
    # save data, labels to file # [NOTE] do something about this ridiculous reshape
    np.save('data.npy', info['data'])
    np.save('labels.npy', np.array(info['labels']))




def run_training_session(clf, iterations: int, trials_per_iteration: int, trial_duration=4, window_size=1000, eeg_source_id='myuid323457', eeg_stream_no=0):
    info = {
        'clf': clf,
        'trial_duration': trial_duration,
        'window_size': window_size,
        'eeg_source_id': eeg_source_id,
        'eeg_stream_no': eeg_stream_no,
        'data': np.empty((0,20, 2000)), # [NOTE]: parameterize or somehow integrate this
        'labels': []
    }

    # initially, train clf on sample data just so it spits out random output for the first collect trial
    print('training on sample data, this data is discarded after the first trial and not used for subsequent training.')
    data = np.load('../../tests/test_data/x_Train_Akima_NF_Dry_EEG3.npy')
    labels = np.load('../../tests/test_data/y_Train_Akima_NF_Dry_EEG3.npy')
    info['clf'].fit(data, labels)
    # remove this ^, have first collect trial use noise trained clf, or no clf and just random nfstim pos

    # start running the classifier process
    print('starting classifier process')
    info['cproc'] = ClassifierProcess(info['clf'], info['eeg_source_id'], window_size=info['window_size'], stream_no=info['eeg_stream_no'])
    info['cproc'].start()

    # initialise classifier inlet
    print('initialising cinlet')
    info['cinlet'] = ClassifierInlet()


    # initialise eeg inlet
    print('looking for stream...')
    streams = resolve_stream('source_id', eeg_source_id)
    info['eeg_inlet'] = StreamInlet(streams[eeg_stream_no])


    # make session
    blocks = [ [collect]*trials_per_iteration, [train] ]*iterations
    sess = Session(info, blocks, use_json=True, hide_info=True)
    print('running session...')
    sess.run()



clf = WrappedCSPLDAClassifier()
run_training_session(clf, 4,16)