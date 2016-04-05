import PointGrid
import Line
import point
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sympy import re, im

class plot(object):
    def __init__(self,grid):
        plt.xlabel('Real')
        plt.ylabel('Imaginary')
        self.fig=plt.figure()
        self.grid=grid
        self.ax = plt.axes(xlim=(self.grid.real_min, self.grid.real_max), ylim=(self.grid.imag_min, self.grid.imag_max))       
        self.line,=self.ax.plot([],[],lw=2)
        self.anim=animation.FuncAnimation(self.fig,self.animate_compute,init_func=self.start,frames=200, blit=True)

    def start(self):
        self.line.set_data([], [])
        return self.line,

    def show(self):
        plt.show()
    
    def save(self,name, video=False, GIF=False):
        return None
        if video:
            anim.save(name+'.mp4', fps=30, extra_args=['-vcodec','libx264'])
    
    def animate_compute(self, step):
        self.line.set_data(self.grid.pre_computed_steps(step-1))
        return self.line,
        
    
    def animate(self):
        self.anim = animation.FuncAnimation(self.fig, self.animate_compute, init_func=self.start,
                               frames=self.grid.n_steps*2, interval=200, blit=True)
       
def add_reverse(target):
    """Take a list, reverse it, and extend the original list with that"""
    og_target = list(target) #copy the list to avoid the next line affecting og_target
    target.reverse()
    return og_target + target