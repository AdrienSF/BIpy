from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_byprop
from multiprocessing import Process
from BIpy.bci.window_inlet import WindowInlet


def run_classifier(clf, in_source_id='17010768', out_source_id='classifier_output', stream_no=0, window_size=None):
    if not window_size:
        if hasattr(clf, 'window_size') and clf.window_size:
            window_size = clf.window_size
        else:
            raise ValueError('Window size must be specified when creating ClassifierProcess if the classifier does not have a window_size attribute.')

    winlet = WindowInlet(in_source_id, window_size=window_size)

    print('creating stream \"'+str(out_source_id)+'\"...')
    info = StreamInfo(source_id=out_source_id)
    outlet = StreamOutlet(info)
    print('done')

    while True:
        outlet.push_sample([clf.predict_proba(winlet.pull_window())])



def ClassifierProcess(clf, in_source_id='17010768', out_source_id='classifier_output', stream_no=0, window_size=500):
    return Process(target=run_classifier, args=(clf, in_source_id, out_source_id, stream_no, window_size))