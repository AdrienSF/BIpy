from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
from multiprocessing import Process
from time import sleep, time
from BIpy.bci.classifer_pocess import ClassifierProcess
from BIpy.bci.inlets import ClassifierInlet
from BIpy.bci.models import DummyClassifier
import math


def send_data():
    # def lsl stream
    print('creating stream \"test_input\"...')
    info = StreamInfo(source_id='test_input')
    outlet = StreamOutlet(info)
    print('done')

    while True:
        sleep(.2)
        sample = time()
        # print('test_input sends:', sample)
        outlet.push_sample([sample])



def test_ClassifierProcess():
    # run lsl input stream
    sproc = Process(target=send_data)
    sproc.start()

    sleep(2)
    # make and run classifier process
    cproc = ClassifierProcess(DummyClassifier(), 'test_input')
    cproc.start()

    sleep(2)
    # make classifier inlet 
    cinlet = ClassifierInlet()

    # send data, assert equals classifier inlet recieved data
    for _ in range(10):
        htime, ttime = time(), cinlet.pull_sample()[0][0]
        print(htime, ttime)
        assert math.isclose(htime, ttime, abs_tol=1e2)
    # terminate process
    sproc.terminate()
    sproc.join()
    cproc.terminate()
    cproc.join()