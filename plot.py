import PointGrid
import Line
import numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sympy import re, im

class plot(object):
    def __init__(self, x_min, x_max, y_min, y_max):
        plt.xlim(x_min, x_max)
        plt.ylim(y_min,y_max)
        plt.xlabel('Real')
        plt.ylabel('Imaginary')
        self.grid=PointGrid()

    def AddLine(self, line):
        #add a line to the pointgrid
        self.grid.addLine(line)

    def NextFrame(self):
        """Deletes the old graph and creates a new one one step ahead"""
        complex_lines=self.grid.NextFrame() #get all the new lines from the grid. The PlotGrid calls to each Line object asking for new points, the Line then calls for new locations from each point based on their deformation pattern.
        for line in complex_lines:
            reals = [re(complex) for complex in line]
            imaginaries = [im(complex) for complex in line] #list comps for the real and imaginary parts of the line
            plt.plot(reals,imaginaries,line.color) #plot this single line on the graph


        