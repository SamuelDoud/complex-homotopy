import PointGrid
import Line
import point
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sympy import re, im
import time 
class plot_window(object):
    def __init__(self,grid):
        self.ranThrough=False
        self.frame_data=[]
        plt.xlabel('Real')
        plt.ylabel('Imaginary')
        self.fig=plt.figure()
        self.grid=grid
        self.ax = plt.axes(xlim=(self.grid.real_min, self.grid.real_max), ylim=(self.grid.imag_min, self.grid.imag_max))       
        self.lines=[self.ax.plot([],[],lw=2)[0] for i in range(len(self.grid.lines))] #create grid.lines number of lines
        self.last = 0
        self.animate()
        

    def start(self):
        for line in self.lines:
           line.set_data([],[])
        return self.lines

    def show(self):
        plt.show()
    
    def save(self,name, video=False, GIF=False):
        return None
        if video:
            anim.save(name+'.mp4', fps=30, extra_args=['-vcodec','libx264'])
        

    def animate_compute(self, step):
        #start_time = time.time()
        #if step < self.last: #are we back at frame 1 are being at frame n>1?
        #    self.ranThrough = True #if true then we have been through the program before
        #else:
        #    if self.ranThrough ==False:
        #        self.last=step #if not, then reset last step 
        #if self.ranThrough: #if we have run through this before, just use precomputed data
        #    self.lines = self.frame_data[step]
        #else:
        #    lines_info = self.grid.pre_computed_steps(step-1) #the first frame is actually frame #1, so subtracting one is needed to align with list indecies
        #    for line_index,line in enumerate(self.lines):#there's probably a pythonic way of doing this
        #        line.set_data(lines_info[0][line_index], lines_info[1][line_index]) #arrange the lines in this step
        #    print("--- %s seconds ---" % (time.time() - start_time))
        #    self.frame_data.append(list(self.lines))#copy of the list so it isnt modified later. also saves this state for later referenece
        lines_info = self.grid.pre_computed_steps(step-1) #the first frame is actually frame #1, so subtracting one is needed to align with list indecies
        for line_index,line in enumerate(self.lines):#there's probably a pythonic way of doing this
            line.set_data(lines_info[0][line_index], lines_info[1][line_index]) #arrange the lines in this step
        return self.lines #return the lines
        
    def next_frame(self, step):
        return self.lines_computed[step-1]

    def animate(self):
        self.anim = animation.FuncAnimation(self.fig, self.animate_compute, init_func=self.start,
                               frames=self.grid.n_steps*2+2, interval=20, blit=True)
       
def add_reverse(target):
    """Take a list, reverse it, and extend the original list with that"""
    og_target = list(target) #copy the list to avoid the next line affecting og_target
    target.reverse()
    return og_target + target