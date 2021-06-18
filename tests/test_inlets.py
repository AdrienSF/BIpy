from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
from multiprocessing import Process
from time import sleep, time
from BIpy.bci.inlets import WindowInlet, ClassifierInlet
import math
import pytest


def send_data(source_id: str):
    # def lsl stream
    info = StreamInfo(source_id=source_id)
    outlet = StreamOutlet(info)

    while True:
        sleep(.2)
        outlet.push_sample([time()])


@pytest.mark.parametrize('window_size', [1, 50])#500, 1500])
def test_WindowInlet(window_size):
    send_proc = Process(target=send_data, args=('test_winlet',))
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



def test_ClassifierInlet():
    send_proc = Process(target=send_data, args=('classifier_output',))
    send_proc.start()

    cinlet = ClassifierInlet()

    for i in range(10):
        htime, ttime = time(), cinlet.pull_sample()[0][0]
        print(htime, ttime)
        assert math.isclose(htime, ttime, abs_tol=1e2)
    send_proc.terminate()
    send_proc.join()
