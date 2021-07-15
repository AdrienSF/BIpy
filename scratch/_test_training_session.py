from BIpy.bci.training_session import TrainingSession
from psychopy import visual, core

win = visual.Window(monitor='testMonitor', fullscr=True)

sess = TrainingSession(win, iterations=2, trials_per_iteration=30 )

sess.run()
win.close()
core.quit()