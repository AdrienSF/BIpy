from BIpy.bci.classifier_inlet import ClassifierInlet
from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
from multiprocessing import Process
from time import sleep, time
from BIpy.bci.window_inlet import WindowInlet
import math
import pytest


def send_data():
    # def lsl stream
    info = StreamInfo(source_id='test_winlet')
    outlet = StreamOutlet(info)

    while True:
        sleep(.002)
        outlet.push_sample([time()])

@pytest.mark.parametrize('window_size', [1, 50])#500, 1500])
def test_WindowInlet(window_size):
    send_proc = Process(target=send_data)
    send_proc.start()

    winlet = WindowInlet(source_id='test_winlet', window_size=window_size)

    for i in range(window_size+10):
        htime, ttimes = time(), winlet.pull_window()

        # check that the data held is no longer than the specified window size
        assert len(ttimes) <= window_size
        # check that the head of the window is the most recent time
        assert math.isclose(htime, ttimes[-1], abs_tol=1e2)

    send_proc.terminate()
    send_proc.join()

