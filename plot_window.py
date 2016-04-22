import math

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
#from multiprocessing import Pool
plt.rcParams['animation.ffmpeg_path'] = 'C:\ffmpeg'

import PointGrid

REAL = 0
IMAG = 1
INDEX = 2

RED = 0
GREEN = 1
BLUE = 2

class plot_window(object):
    """
    This class creates the plot in which the homotopy is displayed.
    Can be used in a tkinter window OR can be used like an API
    """
    def __init__(self,grid, updating_limits = False, start_color = (0.0, 0.0, 1.0), end_color = (1.0, 0.0, 0.0)):
        self.grid = grid #the point grid that this graph is to display. Can be changed!
        self.fig = plt.figure(figsize=(6,6), dpi=100) # the dimmensions of the figure. Could be more intelligent
        plt.ion() #turn on interactive mode. Needed to allow for limit resizing
        #Writer = animation.writers['ffmpeg']
        #self.ffmpeg_writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        self.updating_limits = updating_limits #
        self.new_limits() #take the inital limits from self.grid and apply to the graph
        self.lines = [self.ax.plot([],[],lw=self.grid.lines[line].width)[0] for line in range(self.grid.n_lines)]
        self.ax.set_xlabel("Real")
        self.ax.set_ylabel("Imaginary")
        self._start_color = start_color #private as their is logic to change these colors
        self._end_color = end_color #rbg tuple that specify the color endpoints
        self.color = list(self._start_color) #the color that will actually be displayed
        self.reset_color_diff()

    def set_start_color(self, color_tuple):
        self._start_color = color_tuple
        self.reset_color_diff()

    def set_end_color(self, color_tuple):
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

    def start(self):
        """
        Go to the intial state of the homotopy, namely z.
        """
        return self.animate_compute(0) #Takes what would be the first frame

    def show(self):
        plt.show() #actually display the graph
    
    def save(self,filename, video=False, GIF=False):
        """
        Save the homotopy as a video file or animated image file
        """
        #raise NotImplementedError #need to install FFMPEG
        if video:
            self.anim.save(filename+'.mp4', fps=30, extra_args=['-vcodec','libx264'],writer=self.ffmpeg_writer)
        if GIF:
            raise NotImplementedError 

    def animate_compute(self, step):
        """
        Function that returns the lines that will be used to display this graph.
        """
        if 1 == 0 and self.updating_limits: #not implemented yet
            self.grid.limits_at_step(step)
            self.new_limits()
        [ self.lines[index].set_data(line[REAL],line[IMAG]) for index,line in enumerate(self.grid.pre_computed_steps(step)) ] #this will actually update the graph (on the fly computation) using list comp
        self.color_compute(step)
        for line in self.lines: #apply the color to every line
            line._color = self.color
        #saving this data is too memory intensive for the small amount of computational power required
        return self.lines

    def color_compute(self, step):
        """
        Determine a color based on how far along the animation is.
        """
        if self.grid.n_steps == 1:
            #the graph is not moving. Therefore, its start color is the self_color
            self.color = list(self._start_color)
        else:
            modifier = (math.cos((step/(self.grid.n_steps +1)) * math.pi) + 1) / 2.0 #using a sinsodual curve to change the color
            for index in range(len(self._start_color)):
                self.color[index] = self._start_color[index] + (self.color_diff[index] * modifier)


    def new_limits(self):
        """
        Take the new limits and apply them to the plot.
        """
        self.ax=plt.gca()
        self.ax.set_xlim([self.grid.real_min, self.grid.real_max]) 
        self.ax.set_ylim([self.grid.imag_min, self.grid.imag_max])

    def animate(self,interval_length=20):
        """
        Run the animation through the parameters passed, namely the interval between frames 
        """
        self.anim = animation.FuncAnimation(self.fig, self.animate_compute, init_func=self.start,
                              interval=interval_length, blit=True)