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
        

    