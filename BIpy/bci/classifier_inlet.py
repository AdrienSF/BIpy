from pylsl import StreamInlet, resolve_byprop


class ClassifierInlet():
    def __init__(self, source_id='classifier_output'):
        print("looking for stream \"" + str(source_id) + "\"...")
        streams = resolve_byprop('source_id', source_id, timeout=5)
        if not streams:
            raise TimeoutError('Stream \"' + str(source_id) + '\" not found, timeout expired.')

        self.inlet = StreamInlet(streams[0], max_buflen=1) # max_buflen=1 for real time (samples will be dropped instead instead of buffered)
        print('found')



    def pull_sample(self):
        return self.inlet.pull_sample()