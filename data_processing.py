from  numpy.lib.stride_tricks import sliding_window_view
import numpy as np
import mne
import pyxdf



default_instructed_trigmap = {
    'instructed_left': 12,
    'instructed_right': 13
}

default_free_trigmap = {
    'free_start': 14,
    'free_left': 15,
    'free_right': 16
}









def organize_xdf(xdf_filename: str, trial_duration: float, gelled_indeces=list(range(32,67)), stim_channel=67, instructed_trigger_map=default_instructed_trigmap, free_trigger_map=default_free_trigmap):
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






def get_sliding_window_partition(data, labels, window_size):
    assert len(data.shape) == 3

    windowed_data = np.empty((0,data.shape[2]))
    windowed_labels = []
    for i in range(data.shape[0]):
        trial = data[i]
        print(trial)
        windows = sliding_window_view(trial, (window_size, data.shape[2]))
        true_shape = list(windows.shape)
        true_shape.pop(1)
        true_shape = tuple(true_shape)

        windows = windows.reshape(true_shape)
        print('windows')
        print(windows)
        np.append(windowed_data, windows, axis=0)


        new_labels = np.array([ labels[i] for _ in windows.shape[0] ])
        np.append(windowed_labels, new_labels, axis=0)


    return windowed_data, windowed_labels

    