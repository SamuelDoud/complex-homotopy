import math
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation

REAL = 0
IMAG = 1
INDEX = 2

RED = 0
GREEN = 1
BLUE = 2

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
        self.anim = None
        self.reverse = False
        self.pause = False
        self.frame_number = 0
        self.interval = None
        self.anim = None
        self.grid = grid #the point grid that this graph is to display. Can be changed!
        #the dimmensions of the figure. Could be more intelligent
        self.fig = plt.figure(figsize=(6, 6), dpi=100)
        #clicking the graph fires the launch method
        self.fig.canvas.mpl_connect('button_press_event', self.toggle_pause)
        plt.ion() #turn on interactive mode. Needed to allow for limit resizing
        ffmpeg_animation_writer = animation.writers['ffmpeg']
        self.ffmpeg_writer = ffmpeg_animation_writer(fps=5, bitrate=1800)
        self.updating_limits = updating_limits #
        self.new_limits() #take the inital limits from self.grid and apply to the graph
        self.lines = [self.axes.plot([], [],
                                     lw=self.grid.lines[line].width)[0]
                      for line in range(len(self.grid.lines))]
        self.axes.set_xlabel("Real")
        self.axes.set_ylabel("Imaginary")
        self._start_color = start_color #private as their is logic to change these colors
        self._end_color = end_color #rgb tuple that specify the color endpoints
        self.color = list(self._start_color) #the color that will actually be displayed
        self.reset_color_diff()

    def toggle_pause(self, event):
        """
        Toggles the pause variable through true and false
        """
        #XOR the bool to flip it
        self.pause ^= True

    def pause_animation(self):
        """
        The user has run a command to pause the animation
        For example, opening a grid builder
        """
        self.pause = True

    def resume_animation(self):
        """
        The user has ran a command to resume the animation
        """
        self.pause = False

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

    def save(self, video=False, gif=False):
        """
        Save the homotopy as a video file or animated image file
        """
        #save the frame number the user is currently on
        old_frame_number = self.frame_number
        #jummp to the first frame so this is the first frame of the video
        #need to do this as frame_number is detached from the animation method
        self.frame_number = -1
        #determine if the animation is paused currently
        paused_state = self.pause
        #if the animation is not paused, pause it
        if self.pause:
            self.pause = False
        if video:
            self.anim.save(self.grid.filename + '.mp4', extra_args=['-vcodec', 'libx264'],
                            writer=self.ffmpeg_writer)
        if gif:
            raise NotImplementedError
        #return to the frame that the user was on before they saved
        self.frame_number = old_frame_number
        self.pause = paused_state

    def animate_compute(self, step):
        """
        Function that returns the lines that will be used to display this graph.
        """
        #ignore the step from the animation call!
        #compute if the user has not paused the program
        if not self.pause:
            if len(self.lines) != len(self.grid.lines):
                #there's a new number of lines in the graph
                self.lines = [self.axes.plot([], [],
                                     lw=self.grid.lines[line].width)[0]
                      for line in range(len(self.grid.lines))]
                self.animate()
            self.color_compute(self.frame_number)
            for index, line in enumerate(self.grid.pre_computed_steps(self.frame_number)):
                self.lines[index].set_data(line[REAL], line[IMAG])
                self.lines[index]._color = self.color
            #saving this data is too memory intensive for the small computational power req'd
            #increment the frame number
            self.frame_number += 1
            #set the frame number to the number of steps defined in the grid
            self.frame_number %= self.grid.n_steps
        #time.sleep(.01)
        return self.lines

    def color_compute(self, step):
        """
        Determine a color based on how far along the animation is.
        """
        #workaround for a if the animation is not reversing
        if not self.reverse:
            step /= 2
        if self.grid.n_steps <= 1:
            #the graph is not moving. Therefore, its start color is the self_color
            self.color = list(self._start_color)
            return
        step = step % self.grid.n_steps
        #using a sinsodual curve to change the color
        modifier = (math.cos((2*step/(self.grid.n_steps +1)) * math.pi) + 1) / 2.0
        for index in range(len(self._start_color)):
            self.color[index] = self._end_color[index] - (self.color_diff[index] * modifier)

    def new_limits(self):
        """
        Take the new limits and apply them to the plot.
        """
        self.grid.set_limits()
        self.axes = plt.gca()
        self.axes.set_xlim([self.grid.real_min, self.grid.real_max])
        self.axes.set_ylim([self.grid.imag_min, self.grid.imag_max])

    def animate(self, interval_length=200):
        """
        Run the animation through the parameters passed, namely the interval between frames
        """
        #will call the animation to start at the beginning
        self.interval = interval_length
        del self.anim
        self.anim = animation.FuncAnimation(self.fig, self.animate_compute,
                                            interval=interval_length,
                                            blit=True, frames=self.grid.n_steps)

def show():
    """
    Show the plot. Not really useful in the MainWindow.
    """
    plt.show() #actually display the graph
