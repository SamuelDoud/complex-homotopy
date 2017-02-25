import math
import sys
import os
import shutil
from itertools import cycle

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import images2gif
from PIL import Image

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
    """This class creates the plot in which the homotopy is displayed.
    Can be used in a tkinter window OR can be used like an API."""
    def __init__(self, grid, updating_limits=False,
                 start_color=(0.0, 0.0, 1.0), end_color=(1.0, 0.0, 0.0),
                 row_size=6, column_size=6):
        """Create the intial state of the plot. This will just be the image of z onto z."""
        self.is_paused = False
        self.observers = []
        self.anim = None
        self.reverse = False
        self.pause = False
        self._frame_number = 0
        self.interval = None
        self.anim = None
        self.dpi = 120
        grid.dpi = self.dpi
        self.row_size = row_size
        self.column_size = column_size
        self.grid = grid #the point grid that this graph is to display. Can be changed!
        #the dimmensions of the figure. Could be more intelligent
        self.fig = plt.figure(figsize=(self.column_size, self.row_size), dpi=self.dpi,
                              facecolor="#F0F0F0")
        plt.ion() #turn on interactive mode. Needed to allow for limit resizing
        self.axes = plt.gca()
        #self.axes.axvline(x=0)
        #self.axes.axhline(y=0)
        self.install_ffmpeg = False
        try:
            self.ffmpeg_animation_writer = animation.writers['ffmpeg']
        except:
            self.install_ffmpeg = True
        self.ffmpeg_writer = None
        self.updating_limits = updating_limits #
        self.call_once = 0
        self.imag_spacing = 0.1
        self.real_spacing = 0.1
        self.grid_visible = True
        self.new_limits() #take the inital limits from self.grid and apply to the graph
        self.all_lines = []
        self.lines = [self.axes.plot([], [],
                                     lw=self.grid.lines[line][0].width)[0]
                      for line in range(len(self.grid.lines))]
        self.axes.set_xlabel("Real")
        self.axes.set_ylabel("Imaginary")
        self.fig.tight_layout()
        self._start_color = start_color #private as their is logic to change these colors
        self._end_color = end_color #rgb tuple that specify the color endpoints
        self.color = list(self._start_color) #the color that will actually be displayed
        self.reset_color_diff()
        self.recently_blitted = False
        self.pause_override = False
        self.tracer_lines = []
        self.path_divider = "\\" if os.name == "nt" else "/"
        

    def set_grid_lines(self, real_spacing=None, 
                       imag_spacing=None, line_width=1, visible=None):
        pass

    def toggle_pause(self, event=None):
        """Toggles the pause variable through true and false."""
        #XOR the bool to flip it
        self.pause ^= True
        self.animation_control()
        return self.pause

    def set_animation(self, pause_state):
        """Set the animation's pause variable to the state passed.
        Return the prior state of the pause variable before the call."""
        prior_state = self.pause
        self.pause = pause_state
        self.animation_control()
        return prior_state

    def animation_control(self):
        if self.anim is None:
            return
        if self.pause and not self.is_paused:
            self.anim.event_source.stop()
            self.is_paused = True
        else:
            self.anim.event_source.start()
            self.is_paused = False

    def set_start_color(self, color_tuple):
        """This method changes the start (z) color and updates the difference between the starting
        and ending colors."""
        self._start_color = color_tuple
        self.reset_color_diff()

    def set_end_color(self, color_tuple):
        """This method changes the end (f(z)) color and updates the difference between the starting
        and ending colors."""
        self._end_color = color_tuple
        self.reset_color_diff()

    def reset_color_diff(self):
        """Determine the change in color per step.
        Is called initally and whenever a starting or ending color is changed"""
        self.color_diff = [] #the list that shows how different the colors are per step
        for index in range(len(self._end_color)):
            self.color_diff.append(self._end_color[index] - self._start_color[index])

    def save(self, video=False, gif=False, path=None, frames=25):
        """Save the homotopy as a video file or animated image file"""
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
            self.anim.save(path,
                           writer=self.ffmpeg_writer)
        if gif:
            images = []
            if os.name == "nt":
            #account for the difference between Windows and Unix file systems
                spacer ="\\"
            else:
                spacer = "/"
            frame_dir = "frames" + spacer
            full_frame_directory = resource_path(frame_dir)
            if not os.path.exists(full_frame_directory):
                os.makedirs(full_frame_directory)
            for frame in range(self.grid.n_steps):
                self.animate_compute(frame)
                name = resource_path(frame_dir + "frame" + str(frame) + ".png")
                self.fig.savefig(name)
                images.append(Image.open(name))
            images = images[1:] + [images[0]]
            images2gif.writeGif(filename=path, images=images, duration=[1.0/frames] * self.grid.n_steps, subRectangles=False)
            #delete the frames 
            shutil.rmtree(full_frame_directory)
        self.set_frame(old_frame_number)

    def tracer(self, step, points_to_add):
        for index, line in enumerate(self.tracers):
            line.append(points_to_add[index])
        self.increment_tracer()
        pass

    def increment_tracer(self):
        pass

    def wipe_tracers(self):
        self.tracers = []
        for line in self.lines:
            self.tracers.append([line])

    def animate_compute(self, step):
        """Function that returns the lines that will be used to display this graph."""
        #ignore the step from the animation call!
        #compute if the user has not paused the program
        
        if self.recently_blitted:
            self.un_blit()
        try:
            if not self.pause or self.pause_override and self.lines:
                if len(self.lines) != self.grid.n_lines:
                    #there's a new number of lines in the graph
                    self.lines = [self.axes.plot([], [],
                                                    lw=self.grid.lines[line][LINE].width)[0]
                                    for line in range(self.grid.n_lines)]
                    self.axes.lines = self.lines
                self.color = self.color_compute(self._frame_number)
                for index, line_tuple in enumerate(self.grid.lines):
                    line_object = PointGrid.line_in_tuple(line_tuple)
                    self.lines[index].set_data(*self.grid.computed_steps[self.frame_number][index][:2])
                    self.lines[index]._color = self.grid.computed_steps[self.frame_number][index][2]
                #saving this data is too memory intensive for the small computational power req'd
                #increment the frame number
                if not self.pause_override:
                    self._frame_number += 1
                #set the frame number to the number of steps defined in the grid
                    self._frame_number %= self.grid.n_steps
                    self.set_frame(self.frame_number)
                self.pause_override = False 
            return self.lines
        except IndexError:
            return []
            print(sys.exc_info()[0])

    def blit(self):
        for line in self.lines:
            line.set_visible(False)
        self.recently_blitted = True

    def un_blit(self):
        self.wipe_tracers()
        for line in self.lines:
            line.set_visible(True)
        self.recently_blitted = False
        
    def reset_interval(self, delta):
        """Change the interval by the passed delta."""
        if self.interval > - 1 * delta:
            self.interval += delta
        self.anim._interval = self.interval

    def get_frame(self):
        """Returns the current frame of the homotopy."""
        return self._frame_number

    def set_frame(self, value):
        """A more complex setter method. Starts like a normal setter, then calls every object in the
        observer list with the value."""
        if value >= 0 and value < self.grid.n_steps:
            self._frame_number = value
            for callback in self.observers:
                callback(self._frame_number)

    #property value for frame number
    frame_number = property(get_frame, set_frame)

    def bind(self, callback):
        """Take the object in callback and append it to the observer."""
        self.observers.append(callback)

    def color_compute(self, step):
        """Determine a color based on how far along the animation is."""
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

    def zoom_on_delta(self, delta):
        """zoom in or out by delta which is a value between -1 and 1"""
        self.x_spread = self.grid.real_max - self.grid.real_min
        self.y_spread = self.grid.imag_max - self.grid.imag_min
        self.grid.real_max -= (delta / 2 * self.x_spread)
        self.grid.real_min += (delta / 2 * self.x_spread)
        self.grid.imag_max -= (delta / 2 * self.y_spread)
        self.grid.imag_min += (delta / 2 * self.y_spread)
        self.new_limits()

    def new_limits(self, limits=None):
        """Take the new limits and apply them to the plot."""
        self.axes.set_xlim([self.grid.real_min, self.grid.real_max])
        self.axes.set_ylim([self.grid.imag_min, self.grid.imag_max])
        #since we have a new set of limits the grid lines need to be reconfigured
        self.set_grid_lines()

    def animate(self, interval_length=200):
        """Run the animation through the parameters passed, namely the interval between frames."""
        #will call the animation to start at the beginning
        self.interval = interval_length
        self.anim = animation.FuncAnimation(self.fig, func=self.animate_compute,
                                            #init_func=self.blit,
                                            interval=interval_length,
                                            blit=True, frames=self.grid.n_steps)

    def set_interval(self, interval=40, fps=0):
        """Sets a new interval, or fps, for the animation to run on."""
        if fps > 0:
            interval = 1000 / fps
        if self.anim:
            self.anim._interval = interval
            self.anim.event_source.interval = interval

def resource_path(relative_path):
    """
    A function that gets the absolute path from relative. Needed for redist.
    Found from StackOverflow.
    http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    user: Max
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)