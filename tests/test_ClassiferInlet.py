from BIpy.bci.classifier_inlet import ClassifierInlet
from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
from multiprocessing import Process
from time import sleep, time
from BIpy.bci.classifier_inlet import ClassifierInlet
import math


def send_data():
    # def lsl stream
    info = StreamInfo(source_id='classifier_output')
    outlet = StreamOutlet(info)

    while True:
        sleep(.2)
        outlet.push_sample([time()])

def test_ClassifierInlet():
    send_proc = Process(target=send_data)
    send_proc.start()

    cinlet = ClassifierInlet()

    for i in range(10):
        htime, ttime = time(), cinlet.pull_sample()[0][0]
        print(htime, ttime)
        assert math.isclose(htime, ttime, abs_tol=1e2)
    send_proc.terminate()
    send_proc.join()
