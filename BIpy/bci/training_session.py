import numpy as np

from BIpy.session import Session
from BIpy.stims import NeuroFeedbackStim
from BIpy.classifier_process import ClassifierProcess
from BIpy.inlets import ClassifierInlet
from BIpy.data_processing import get_sliding_window_partition

from psychopy import visual, core, event

text_stim = visual.TextStim(win)

def collect(logger):
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
    data = []
    predict_probas = []
    clock = core.Clock()
    while clock.getTime() < info['trial_duration']:
        # neurofeedback
        prob = info['cinlet'].pull_sample[0][1]
        info['nf_stim'].draw(prob)
        win.flip()
        data = data + info['eeg_inlet'].pull_chunk()[0][0]
        predict_probas.append(prob)


    # ask for label
    text_stim.text = 'Which side were you imagining? press 1 for left and 0 for right'
    text_stim.draw()
    win.flip()
    key = event.waitKeys(keyList=['0', '1'])
    label = int('0' in key)

    # append label and data to info
    info['data'] = info['data'] + data
    info['labels'].append(label)

    # log true label and list of predict proba?
    logger.log({'label': label, 'predict_probas': predict_probas})

def train(logger):
    logger.hide_trial()
    info = logger.info
    # kill old classifier (if there is one)
    if 'cproc' in info and info['cproc']:
        info['cproc'].kill()
        info['cproc'].close()
    # split data into the right size chunks for clf input
    data, labels = get_sliding_window_partition(np.array(info['data']), np.array(info['labels']), window_size=500)
    # re-train model
    info['clf'].fit(data, labels)
    # re-start classifier process
    info['cproc'] = ClassifierProcess(info['clf'], info['eeg_source_id'], window_size=info['window_size'], stream_no=info['eeg_stream_no'])
    info['cproc'].start()

    # make new classifier inlet in case the previos timed out
    info['cinlet'] = ClassifierInlet()
    
    # save data, labels to file
    np.save('data.npy', np.array(info['data']))
    np.save('labels.npy', np.array(info['labels']))




def get_training_session(clf, iterations: int, trials_per_iteration: int, trial_duration=4, window_size=500, eeg_source_id='myuid323457', eeg_stream_no=0):
    info = {
        'clf': clf,
        'iterations':  iterations,
        'trials_per_iteration': trials_per_iteration,
        'trial_duration': trial_duration,
        'window_size': window_size,
        'eeg_source_id': eeg_source_id,
        'eeg_stream_no': eeg_stream_no
    }