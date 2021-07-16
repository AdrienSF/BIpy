import numpy as np
import random
import gc

from BIpy.session import Session
from BIpy.data_processing import get_windows, LowpassWrapper
from BIpy.bci.stims import NeuroFeedbackStim
# from BIpy.bci.classifier_process import ClassifierProcess
from classifier_process import ClassifierProcess
from BIpy.bci.inlets import ClassifierInlet
# from BIpy.bci.models import WrappedCSPLDAClassifier
from models import WrappedCSPLDAClassifier

from psychopy import visual, core, event
from pylsl import StreamInlet, resolve_stream

# ####
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import Pipeline
from mne.decoding import CSP
# ####



def TrainingSession(win, iterations: int, trials_per_iteration: int, clf=WrappedCSPLDAClassifier(), trial_duration=4, sampling_rate=500, data_channels=list(range(20)), window_size=500, step_size=100, eeg_source_id='myuid323457', eeg_stream_no=0, resolution=6):
    
    def kill(logger):
        logger.hide_trial()
        info = logger.info
        # save data
        # save data, labels to file
        np.save('data.npy', info['data'])
        np.save('labels.npy', np.array(info['labels']))

        # kill old classifier (if there is one)
        if 'cproc' in info and info['cproc']:
            info['cproc'].kill()
            info['cproc'].join()
            info['cproc'].close()
            
            
    def collect(logger):
        print('starting collect trial')
        info = logger.info

        # ask to start
        text_stim.text = 'Press any key to start.'
        text_stim.draw()
        window.flip()
        event.waitKeys()
        window.flip()
        # 2 sec delay
        core.wait(2)
        # loop for 4 seconds neurofeedback, start recording eeg data
        trial_data = []
        predict_probas = []
        clock = core.Clock()
        print('starting trial loop')
        # wait until classifier process is ready to start classifying
        info['cinlet'].pull_sample()
        # clear eeg lsl buffer
        info['eeg_inlet'].pull_chunk(max_samples=int(1e6))
        while clock.getTime() < info['trial_duration'] or len(trial_data) < info['samples_per_trial']:
            # neurofeedback
            prob = info['cinlet'].pull_sample()[0][0] # sample = [[prob], timestamp]
            # print('pulled sample:', prob)
            nf_stim.draw(prob)
            window.flip()
            trial_data = trial_data + info['eeg_inlet'].pull_chunk()[0]
            predict_probas.append(prob)


        # ask for label
        text_stim.text = 'Which side were you imagining? press 1 for left and 0 for right'
        text_stim.draw()
        window.flip()
        key = event.waitKeys(keyList=['0', '1'])
        label = int('0' in key)

        # append label and data to info
        # change trial data to mne's CSP input format
        print('untrimmed trial_data shape:', np.array(trial_data).shape)

        trial_data = np.transpose(np.array(trial_data)[:info['samples_per_trial'],info['data_channels']])
        print('trial_data shape:', trial_data.shape)
        info['data'] = np.vstack((info['data'], [trial_data]))
        info['labels'].append(label)
        print('[collect]: data shape:', np.array(info['data']).shape)
        # log true label and list of predict proba
        logger.log({'label': label, 'predict_probas': predict_probas})

    def train(logger):
        logger.hide_trial()
        info = logger.info
        # kill old classifier (if there is one)
        if 'cproc' in info and info['cproc']:
            info['cproc'].kill()
            info['cproc'].join()
            info['cproc'].close()
        # split data into the right size chunks for clf input
        print('[train]: data shape:', np.array(info['data']).shape)
        gc.collect()
        data, labels = get_windows(np.array(info['data']), np.array(info['labels']), info['window_size'], step_size=100)
        print('windowed data shape:', data.shape)
        # re-train model
        info['clf'].fit(data, labels)
        # re-start classifier process
        info['cproc'] = ClassifierProcess(info['clf'], info['eeg_source_id'], window_size=info['window_size'], stream_no=info['eeg_stream_no'])
        info['cproc'].start()

        # make new classifier inlet in case the previos timed out
        info['cinlet'] = ClassifierInlet()
        gc.collect()
        
        # save data, labels to file
        np.save('data.npy', info['data'])
        np.save('labels.npy', np.array(info['labels']))
    
    
    
    
    
    
    window = win
    text_stim = visual.TextStim(window)
    nf_stim = NeuroFeedbackStim(window, resolution)

    samples_per_trial = trial_duration*sampling_rate
    info = {
        'clf': clf,
        'trial_duration': trial_duration,
        'window_size': window_size,
        'eeg_source_id': eeg_source_id,
        'eeg_stream_no': eeg_stream_no,
        'sampling_rate': sampling_rate,
        'samples_per_trial': samples_per_trial,
        'data_channels': data_channels,
        'data': np.empty((0,len(data_channels), samples_per_trial)), # [NOTE]: parameterize or somehow integrate this
        'labels': []
    }

    
    # initialise eeg inlet
    print('looking for eeg stream...')
    streams = resolve_stream('source_id', eeg_source_id)
    info['eeg_inlet'] = StreamInlet(streams[eeg_stream_no])
    print('found')

    ########## INITIALIZE CLASSIFIER ##########
    # train initial classifier on noise
    print('collecting noise...')
    trial_data = []
    clock = core.Clock()
    while clock.getTime() < info['trial_duration']*2 or len(trial_data) < samples_per_trial*2:
        chunk = info['eeg_inlet'].pull_chunk()[0]
        # print('chunk shape:', np.array(chunk).shape)
        trial_data = trial_data + chunk

    # crop noise
    trial_data = np.array(trial_data)
    print('trail data shape:', trial_data.shape)
    trial_data = trial_data[:,data_channels]
    trial_data = trial_data[:samples_per_trial*2]
    # split, transpose and label noise arbitrarily
    data = np.array([ np.transpose(trial_data[:samples_per_trial]), np.transpose(trial_data[-samples_per_trial:]) ])
    labels = np.array([1,0])
    # just partitioning this won't give enough data to run csp, so we'll run a sliding window over it
    data, labels = get_windows(data, labels, window_size, step_size)
    # train classifier on noise
    print('training initial classifier on noise...')
    print('data shape:', data.shape)
    print('labels shape:', labels.shape)
    clf.fit(data, labels)
    ########## INITIALIZE CLASSIFIER ##########


    # start running the classifier process
    print('starting classifier process')
    info['cproc'] = ClassifierProcess(info['clf'], info['eeg_source_id'], window_size=info['window_size'], stream_no=info['eeg_stream_no'])
    info['cproc'].start()

    # initialise classifier inlet
    print('initialising cinlet')
    info['cinlet'] = ClassifierInlet()


    # make and return session
    blocks = [[collect]*trials_per_iteration] + [ [train], [collect]*trials_per_iteration ]*(iterations-1) + [[kill]]
    return Session(info, blocks, use_json=True, hide_info=True)
