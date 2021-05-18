from pylsl import StreamInlet, resolve_byprop

from time import sleep, time

class WindowInlet():
    def __init__(self, source_id='17010768', stream_no=0, window_size=500):
        print("looking for stream \"" + str(source_id) + "\"...")
        streams = resolve_byprop('source_id', source_id, timeout=5) # for ActiChamp - 17010768 ||||| portable: myuid323457
        if not streams:
            raise TimeoutError('Stream \"' + str(source_id) + '\" not found, timeout expired.')

        self.inlet = StreamInlet(streams[stream_no]) # for ActiChamp (I think streams[1]) |||| streams[0] for portable
        print('found')

        self.window_size = window_size
        self.window = []

        self.pull_window()



    def pull_window(self, window_size=None, timeout=0.25):
        if not window_size:
            window_size = self.window_size
        # should take all buffered data
        chunk = self.inlet.pull_chunk(timeout=timeout, max_samples=10000)[0]
        # chunk = self.inlet.pull_sample()[0]
        # if no data is buffered, return
        if not chunk:
            return
        print('chunk:', chunk)
        self.window = self.window + chunk[0]
        print('window', self.window)

        # trim to window size
        if len(self.window) > self.window_size:
            excess = len(self.window) - self.window_size
            self.window = self.window[excess:]


        print('window', self.window)
        return self.window
