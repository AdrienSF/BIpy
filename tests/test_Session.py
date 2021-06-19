from BIpy.session import Session
import pytest
import os

# @pytest.mark.parametrize('window_size', [1, 50])#500, 1500])
def test_run():
    trial = lambda logger : None
    blocks = [[trial], [trial,trial]]
    info = {'id': 'test'}

    session = Session(info, blocks)
    session.run()


def test_log():
    blocks = [[lambda logger : logger.log({1:1}, save_to_file=False)],[lambda logger : logger.log({2:2}, save_to_file=False),lambda logger : logger.log({3:3}, save_to_file=False)]]
    info = {'id': 'test'}

    session = Session(info, blocks)
    session.run()


    assert session.log_history[0][0] == {'1':1}
    assert session.log_history[1][0] == {'2':2}
    assert session.log_history[1][1] == {'3':3}


def test_hide_trial():
    blocks = [[lambda logger : logger.hide_trial()],[lambda logger : logger.log({2:2}, save_to_file=False),lambda logger : logger.log({3:3}, save_to_file=False)]]
    info = {'id': 'test'}

    session = Session(info, blocks)
    session.run()


    assert session.log_history[0][0] == dict()
    assert session.log_history[1][0] == {'2':2}
    assert session.log_history[1][1] == {'3':3}


def test_save():
    blocks = [[lambda logger : logger.log({1:1})],[lambda logger : logger.log({2:2}),lambda logger : logger.log({3:3})]]
    info = {'id': 'test'}

    session = Session(info, blocks)
    session.run()

    with open('idtest.csv') as f:
        with open('tests/test_data/ref.csv') as ref:
            assert f.read() == ref.read()

    os.remove('idtest.csv')

    


def test_save_hidden():
    blocks = [[lambda logger : logger.hide_trial()],[lambda logger : logger.log({2:2}),lambda logger : logger.log({3:3})]]
    info = {'id': 'test'}

    session = Session(info, blocks)
    session.run()

    with open('idtest.csv') as f:
        with open('tests/test_data/hidref.csv') as ref:
            assert f.read() == ref.read()

    os.remove('idtest.csv')

