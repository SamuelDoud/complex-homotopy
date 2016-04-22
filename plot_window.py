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
    """This class creates the plot in which the homotopy is displayed"""
    def __init__(self,grid):
        self.grid = grid
        self.fig = plt.figure(figsize=(6,6), dpi=100)
        plt.ion()
        #Writer = animation.writers['ffmpeg']
        #self.ffmpeg_writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        self.updating_limits = True
        self.new_limits()
        self.lines = [self.ax.plot([],[],lw=self.grid.lines[line].width)[0] for line in range(self.grid.n_lines)]
        self.ax.set_xlabel("Real")
        self.ax.set_ylabel("Imaginary")
        self.start_color = (0.0, 0.0, 1.0)
        self.end_color = (1.0, 0.0, 0.0) #rbg tuple
        self.color = list(self.start_color) #the color that will actually be displayed
        self.color_diff = []
        for index in range(len(self.end_color)):
            self.color_diff.append(self.end_color[index] - self.start_color[index])

    def start(self):
        """Go to the intial state"""
        return self.animate_compute(0) #Takes what would be the first frame

    def show(self):
        plt.show() #actually display the graph
    
    def save(self,name, video=False, GIF=False):
        """
        Save the homotopy as a video file or animated image file
        """
        #raise NotImplementedError #need to install FFMPEG
        if video:
            self.anim.save(name+'.mp4', fps=30, extra_args=['-vcodec','libx264'],writer=self.ffmpeg_writer)
        if GIF:
            raise NotImplementedError 

    def set_line(self,data):
        self.lines[data[INDEX]].set_data(data[REAL],data[IMAG])

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
        modifier = (math.cos((step/(self.grid.n_steps +1)) * math.pi) + 1) / 2.0 #using a sinsodual curve to change the color
        for index in range(len(self.start_color)):
            self.color[index] = self.start_color[index] + (self.color_diff[index] * modifier)


    def new_limits(self):
        """
        Take the new limits and apply them to the plot.
        """
        self.ax=plt.gca()
        self.ax.set_xlim([self.grid.real_min, self.grid.real_max]) #something is cooky here
        self.ax.set_ylim([self.grid.imag_min, self.grid.imag_max])

    def animate(self,interval_length=20):
        """
        Run the animation through the parameters passed, namely the interval between frames 
        """
        self.anim = animation.FuncAnimation(self.fig, self.animate_compute, init_func=self.start,
                              interval=interval_length, blit=True)