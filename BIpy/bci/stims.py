from psychopy import visual, core, event
import math


class NeuroFeedbackStim():
    """Progress bar style stim for displaying classifier output to the subject

    Methods
    -------
    draw(self, porportion=None)
        draws the stim
    
    """    

    def __init__(self, win, resolution: int):
        """
            Parameters
            ----------
            win : Psychopy.visual.Window()
                window in which the stim will be drawn
            resolution : int
                number of segments in on each side of the "progress bar"
        """
        
        self.window = win
        self.resolution = resolution
        self.frame_width = .8*2
        self.frame_height = .2
        self.seg_width = self.frame_width/(2*resolution)

        self.frame = visual.rect.Rect(win, lineColor='Black', size=(self.frame_width, self.frame_height))

        self.segments = []
        for i in range(resolution):
            l = visual.rect.Rect(win, fillColor='red', size=(self.seg_width, self.frame_height), pos=(-(i+.5)*self.seg_width, 0))
            r = visual.rect.Rect(win, fillColor='red', size=(self.seg_width, self.frame_height), pos=((i+.5)*self.seg_width, 0))

            self.segments.insert(0, l)
            self.segments.append(r)


    def draw(self, proportion=None):
        """draws the stim

            Parameters
            ----------
            proportion : float, default None
                value between 0 and 1. At 0 the "progress bar" reaches all the way to the left, and at 1 it reaches the right
                
        """
        
        if proportion == None:
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
