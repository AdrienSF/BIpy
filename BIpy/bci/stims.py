from psychopy import visual, core, event
import math


class NeuroFeedbackStim():
    def __init__(self, win, resolution):
        self.window = win
        self.resolution = resolution
        self.frame_width = .8*2
        self.frame_height = .2
        self.seg_width = self.frame_width/(2*resolution)

        self.frame = visual.rect.Rect(win, lineColor='blue', size=(self.frame_width, self.frame_height))

        self.segments = []
        for i in range(resolution):
            l = visual.rect.Rect(win, fillColor='red', size=(self.seg_width, self.frame_height), pos=(-(i+.5)*self.seg_width, 0))
            r = visual.rect.Rect(win, fillColor='red', size=(self.seg_width, self.frame_height), pos=((i+.5)*self.seg_width, 0))

            self.segments.insert(0, l)
            self.segments.append(r)


    def draw(self, proportion=None):
        print("I'm trying to draw myself!")
        if not proportion:
            for seg in self.segments:
                seg.draw()
            self.frame.draw()
            return

        if proportion < .5:
            l = math.floor(proportion*len(self.segments))
            r = int(len(self.segments)/2)
        else:
            r = math.ceil(proportion*len(self.segments))
            l = int(len(self.segments)/2)

        for seg in self.segments[l:r]:
            seg.draw()
        self.frame.draw()
