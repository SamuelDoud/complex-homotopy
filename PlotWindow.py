import math
from itertools import cycle

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import Line
import PointGrid

REAL = 0
IMAG = 1
INDEX = 2

RED = 0
GREEN = 1
BLUE = 2

LINE = 0

PAUSE = True
PLAY = False

class PlotWindow(object):
    """
    This class creates the plot in which the homotopy is displayed.
    Can be used in a tkinter window OR can be used like an API
    """
    def __init__(self, grid, updating_limits=False,
                 start_color=(0.0, 0.0, 1.0), end_color=(1.0, 0.0, 0.0)):
        """
        Create the intial state of the plot. This will just be the image of z onto z.
        """
        self.observers = []
        self.anim = None
        self.reverse = False
        self.pause = False
        self._frame_number = 0
        self.interval = None
        self.anim = None
        self.dpi = 100
        self.grid = grid #the point grid that this graph is to display. Can be changed!
        grid.dpi = self.dpi
        #the dimmensions of the figure. Could be more intelligent
        self.fig = plt.figure(figsize=(7, 7), dpi=self.dpi)
        plt.ion() #turn on interactive mode. Needed to allow for limit resizing
        self.ffmpeg_animation_writer = animation.writers['ffmpeg']
        self.ffmpeg_writer = None
        self.updating_limits = updating_limits #
        self.new_limits() #take the inital limits from self.grid and apply to the graph
        self.all_lines = []
        self.lines = [self.axes.plot([], [],
                                     lw=self.grid.lines[line][0].width)[0]
                      for line in range(len(self.grid.lines))]
        self.axes.set_xlabel("Real")
        self.axes.set_ylabel("Imaginary")
        self._start_color = start_color #private as their is logic to change these colors
        self._end_color = end_color #rgb tuple that specify the color endpoints
        self.color = list(self._start_color) #the color that will actually be displayed
        self.reset_color_diff()
        self.recently_blitted = False
        self.pause_override = False

    def toggle_pause(self, event):
        """
        Toggles the pause variable through true and false
        """
        #XOR the bool to flip it
        self.pause ^= True

    def set_animation(self, pause_state):
        """
        Set the animation's pause variable to the state passed.
        Return the prior state of the pause variable before the call.
        """
        prior_state = self.pause
        self.pause = pause_state
        return prior_state

    def set_start_color(self, color_tuple):
        """
        This method changes the start (z) color and updates the difference between the starting
        and ending colors.
        """
        self._start_color = color_tuple
        self.reset_color_diff()

    def set_end_color(self, color_tuple):
        """
        This method changes the end (f(z)) color and updates the difference between the starting
        and ending colors.
        """
        self._end_color = color_tuple
        self.reset_color_diff()

    def reset_color_diff(self):
        """
        Determine the change in color per step.
        Is called initally and whenever a starting or ending color is changed
        """
        self.color_diff = [] #the list that shows how different the colors are per step
        for index in range(len(self._end_color)):
            self.color_diff.append(self._end_color[index] - self._start_color[index])

    def save(self, video=False, gif=False, frames=25):
        """
        Save the homotopy as a video file or animated image file
        """
        #save the frame number the user is currently on
        old_frame_number = self._frame_number
        #jummp to the first frame so this is the first frame of the video
        #need to do this as frame_number is detached from the animation method
        self._frame_number = -1
        #determine if the animation is paused currently
        was_paused = self.set_animation(PAUSE)
        #if the animation is not paused, pause it
        if self.pause:
            self.pause = False
        if video:
            self.ffmpeg_writer = self.ffmpeg_animation_writer(fps=frames, bitrate=1800)
            del self.anim
            self.animate(self.interval)
            self.anim.frame_seq = cycle(range(self.grid.n_steps))
            self.anim.save(self.grid.filename + '.mp4', extra_args=['-vcodec', 'libx264'],
                           writer=self.ffmpeg_writer)
        if gif:
            raise NotImplementedError
        #return to the frame that the user was on before they saved
        self._frame_number = old_frame_number
        self.set_animation(was_paused)

    def animate_compute(self, step):
        """
        Function that returns the lines that will be used to display this graph.
        """
        #ignore the step from the animation call!
        #compute if the user has not paused the program
        if self.recently_blitted:
            self.un_blit()
        if not self.pause or self.pause_override:
            if len(self.lines) != self.grid.n_lines:
                #there's a new number of lines in the graph
                self.lines = [self.axes.plot([], [],
                                                lw=self.grid.lines[line][LINE].width)[0]
                                for line in range(self.grid.n_lines)]
                self.axes.lines = self.lines
            self.color = self.color_compute(self._frame_number)
            for index, line_tuple in enumerate(self.grid.lines):
                line_object = PointGrid.line_in_tuple(line_tuple)
                self.lines[index].set_data(*self.grid.computed_steps[self.frame_number][index])
                if line_object.color:
                    self.lines[index]._color = line_object.color
                else:
                    self.lines[index]._color = self.color
                self.lines[index]
                
                #self.lines[index].set_visible(True)
            #saving this data is too memory intensive for the small computational power req'd
            #increment the frame number
            if not self.pause_override:
                self._frame_number += 1
            #set the frame number to the number of steps defined in the grid
                self._frame_number %= self.grid.n_steps
                self.set_frame(self.frame_number)
            self.pause_override = False
        return self.lines

    def blit(self):
        for line in self.lines:
            line.set_visible(False)
        self.recently_blitted = True

    def un_blit(self):
        for line in self.lines:
            line.set_visible(True)
        self.recently_blitted = False

    def reset_interval(self, delta):
        """
        Change the interval by the passed delta
        """
        if self.interval > - 1 * delta:
            self.interval += delta
        self.anim._interval = self.interval

    def get_frame(self):
        """
        Returns the current frame of the homotopy
        """
        return self._frame_number

    def set_frame(self, value):
        """
        A more complex setter method. Starts like a normal setter, then calls every object in the
        observer list with the value.
        """
        if value >= 0 and value < self.grid.n_steps:
            self._frame_number = value
            for callback in self.observers:
                callback(self._frame_number)

    #property value for frame number
    frame_number = property(get_frame, set_frame)

    def bind(self, callback):
        """
        take the object in callback and append it to the observer
        """
        self.observers.append(callback)

    def color_compute(self, step):
        """
        Determine a color based on how far along the animation is.
        """
        color = list(self._start_color)
        #workaround for a if the animation is not reversing
        if not self.reverse:
            step /= 2
        if self.grid.n_steps <= 1:
            #the graph is not moving. Therefore, its start color is the self_color
            return color
        step = step % self.grid.n_steps
        #using a sinsodual curve to change the color
        modifier = (math.cos((2*step/(self.grid.n_steps +1)) * math.pi) + 1) / 2.0
        for index in range(len(self._start_color)):
            color[index] = self._end_color[index] - (self.color_diff[index] * modifier)
        return color

    def new_limits(self):
        """
        Take the new limits and apply them to the plot.
        """
        self.axes = plt.gca()
        self.axes.set_xlim([self.grid.real_min, self.grid.real_max])
        self.axes.set_ylim([self.grid.imag_min, self.grid.imag_max])

    def animate(self, interval_length=200):
        """
        Run the animation through the parameters passed, namely the interval between frames
        """
        #will call the animation to start at the beginning
        self.interval = interval_length
        self.anim = animation.FuncAnimation(self.fig, func=self.animate_compute,
                                            #init_func=self.blit,
                                            interval=interval_length,
                                            blit=True, frames=self.grid.n_steps)
