from training_session import TrainingSession
from psychopy import visual, core

win = visual.Window(monitor='testMonitor', fullscr=True)

sess = TrainingSession(win, 1, 2)

sess.run()
win.close()
core.quit()