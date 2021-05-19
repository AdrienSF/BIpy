from BIpy.bci.data_processing import get_sliding_window_partition
import numpy as np

def test_sliding_window_partition():
    dat = np.arange(40*5).reshape((5,10,4))
    lab = np.array([ i%2 for i in range(5)])
    print('shape:', dat.shape)

    data, labels = get_sliding_window_partition(dat, lab, window_size=5)
    print('data')
    print(data)
    print('labels')
    print(labels)
    assert False
# test_sliding_window_partition()