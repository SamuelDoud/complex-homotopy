import Line
import function
from sympy import re, im, Symbol, symbols, I
import numpy as np
import random

REAL=0
IMAG=1 #constants for consistent iterable access

class PointGrid(object):
    """Point Grid holds all the points on the graph and their associations"""
    def __init__(self, corner_upper_left, corner_lower_right, n_lines, n_points):
        self.lines =[]
        self.n_lines = n_lines
        self.n_steps = 1
        self.n_points = n_points

        self.real_step = (self.lower_right.real - self.upper_left.real) / n_lines
        self.imaginary_step = (self.lower_right.imag - self.upper_left.imag) / n_lines
        self.z = symbols('z',complex=True)
        self.real_max=None
        self.real_min=None
        self.imag_max=None
        self.imag_min=None
    
        
    def grid_lines(self,complex_high_imag_low_real, complex_low_imag_high_real,n_lines,n_points_per_line):
        group = 
        self.draw_real(complex_high_imag_low_real, complex_low_imag_high_real,n_lines,n_points_per_line)
        self.draw_imag(complex_high_imag_low_real, complex_low_imag_high_real,n_lines,n_points_per_line)

    def draw_real(self,complex_high_imag_low_real, complex_low_imag_high_real,n_lines,n_points_per_line):
        """Draw the lines with constant re(z)"""
        upper = complex(self.upper_left.real,self.upper_left.imag)
        lower = complex(self.upper_left.real,self.lower_right.imag)#inital states of the lower and upper bound of the line
        for step in range(self.n_lines+1): #draw a line for the number of steps determined by the user            
            f_re_z = function.function(re(upper)+im(self.z)*I)#create a function (this may be improved if I can determine that adding x to f_re_z is possible)
            line = Line.Line(f_re_z,upper,lower,self.n_points,self.n_points,"blue") #create a line with starting points given
            self.add_line(line) #add the line to the list at large
            upper += complex(self.real_step,0)
            lower += complex(self.real_step,0) #shift the line on the real axis by real step

    def draw_imag(self,complex_high_imag_low_real, complex_low_imag_high_real,n_lines,n_points_per_line):
        """Draw the lines with constant im(z)"""
        upper = np.linspace(self.complex_high_imag_low_real,complex_low_imag_high_real.imag,n_lines+1)#the initial states of the upper and lower bounds of the line
        lower = np.linspace(self.complex_low_imag_high_real.real,complex_high_imag_low_real.imag,n_lines+1)
        for step in range(self.n_lines+1):
            f_im_z = function.function(re(self.z)+complex(0,(upper[step].imag)))
            line = Line.Line(f_im_z,upper[step],lower[step],n_points,n_points,"red")
            self.add_line(line)
   
    def add_line(self, line):
        self.lines.append(line)#add the new Line object to the list

    def removeLine(self, line_name):
        #line names share prefixes and gradually get more specific....
        #standard.. "LINE_TypeOfLine_setName_LineNumber"
        #if the user calls x.remove("LINE"), then all lines are removed
        #but more specific calls can be made
        for i, line in enumerate(self.lines): #take every line in the lines list and store the line into line and save to the index to i
            if line.name.startswith(line_name):#check if the Line object's name matches the deletion standard
                del self.lines[i] #if it does, delete it from the list
    
    def lines_at_step(self, n):
        """Get the state of every line at this current state"""
        return [ln.points_at_step(n) for ln in self.lines]

    def pre_compute(self):
        """Take every lines order and save it in an easily accessible list so computation doesn't have to be performed on the fly.
        Also, this function will track the min/max of both the real and imaginary axis"""
        self.computed_steps =[]
        self.real_min=self.lines[0].points[0].point_order[REAL][0]
        self.real_max=self.lines[0].points[0].point_order[REAL][0]
        self.imag_min=self.lines[0].points[0].point_order[IMAG][0]
        self.imag_max=self.lines[0].points[0].point_order[IMAG][0]
        for n in range(self.n_steps*2+2): #go through every step in the lines. n_steps * 2 because we are collecting the reversal steps too
            self.computed_steps.append(self.lines_at_step(n))#add that tuple to the precomputed list
        self.set_limits()

    def set_limits(self):
        for step in self.computed_steps:
            for line in step:
                temp_max = max(line[REAL])
                temp_min = min(line[REAL])
                if temp_max > self.real_max:
                    self.real_max = temp_max
                if temp_min < self.real_min:
                    self.real_min = temp_min
                temp_max = max(line[IMAG])
                temp_min = min(line[IMAG])
                if temp_max > self.imag_max:
                    self.imag_max = temp_max
                if temp_min < self.imag_min:
                    self.imag_min = temp_min
        pad=1.05 #add 5% so the window isn't cramped. Now that I think about it.. there is a more pythonic way to do this
        self.force_square()
        self.real_max*=pad
        self.real_min*=pad
        self.imag_max*=pad
        self.imag_min*=pad

    def force_square(self):
        """
        Force the min-maxes to form a square.
        """
        real_diff=self.real_max-self.real_min
        imag_diff=self.imag_max-self.imag_min
        if real_diff > imag_diff:
            self.imag_max-=((real_diff-imag_diff)*2)
            self.imag_min+=((real_diff-imag_diff)*2)
        else:
            self.real_max-=((imag_diff-real_diff)*2)
            self.real_min+=((imag_diff-real_diff)*2)

    def pre_computed_steps(self,n):
        """get the precomputed step n"""
        return self.computed_steps[n % (self.n_steps * 2+1)]

    def provide_function(self,function,n):
        """Give a complex function to this function.
        Then, operate on each point by the function
        (1-(t/n))point + (t/n)*f(point) where t is the step in the function 
        after this function is completed, all the points will have their homotopy computed"""
        self.n_steps=n
        for line_index in range(len(self.lines)):
            self.lines[line_index].parameterize_points(function,n)
        self.pre_compute()#set the steps now so the program doesn't have to do this on the fly

         