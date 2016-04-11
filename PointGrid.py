import Line
import function
from sympy import re, im, arg, Abs, Symbol, symbols, I
import numpy as np

REAL=0
IMAG=1 #constants for consistent iterable access

class PointGrid(object):
    """Point Grid holds all the points on the graph and their associations"""
    def __init__(self, corner_upper_left, corner_lower_right, n_lines, n_points):
        self.lines =[]
        self.n_steps = 1
        self.n_lines=0
        self.group_counter=0
        self.z = symbols('z',complex=True)
        self.draw_lines()
        self.real_max=None
        self.real_min=None
        self.imag_max=None
        self.imag_min=None
        
    def draw_lines(self):
        self.draw_real()
        self.draw_imag()

    def draw_real(self,complex_high_imag_low_real, complex_low_imag_high_real,n_lines,n_points_per_line):
        """Draw the lines with constant re(z)"""
        upper = np.linspace(complex_high_imag_low_real,complex(complex_low_imag_high_real.real,complex_high_imag_low_real.imag),n_lines)#the initial states of the upper and lower bounds of the line
        lower = np.linspace(complex(complex_high_imag_low_real.real,complex_low_imag_high_real.imag),complex_low_imag_high_real,n_lines)
        for step in range(n_lines): #draw a line for the number of steps determined by the user            
            f_re_z = function.function(re(upper[step])+im(self.z)*I)#create a function (this may be improved if I can determine that adding x to f_re_z is possible)
            line = Line.Line(f_re_z,upper[step],lower[step],n_points_per_line,"blue",self.group_counter) #create a line with starting points given
            self.add_line(line) #add the line to the list at large

    def draw_imag(self,complex_high_imag_low_real, complex_low_imag_high_real,n_lines,n_points_per_line):
        """Draw the lines with constant im(z)"""
        upper = np.linspace(complex_high_imag_low_real, complex(complex_high_imag_low_real.real,complex_low_imag_high_real.imag),n_lines)#the initial states of the upper and lower bounds of the line
        lower = np.linspace(complex(complex_low_imag_high_real.real,complex_high_imag_low_real.imag),complex_low_imag_high_real,n_lines)
        for step in range(n_lines):
            f_im_z = function.function(re(self.z)+complex(0,(upper[step].imag)))
            line = Line.Line(f_im_z,upper[step],lower[step],n_points_per_line,"red",self.group_counter)
            self.add_line(line)
   
    def add_line(self, line):
        self.lines.append(line)#add the new Line object to the list
        self.n_lines+=1

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
        """
        Go through every step and find the min/max of both the imaginary and real parts and set these as teh limits of the graph.
        This can be overrrode by the user if they input custom limits.
        """
        if self.limits:
            pass #the user provided limits if self.limits is not equal to None. Therefore, this function is not to be executed
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
        return self.computed_steps[n % (self.n_steps * 2+1)] #return the step n using a modulo the number of steps so that an overflow is not possible.

    def provide_function(self,function,n):
        """Give a complex function to this function.
        Then, operate on each point by the function
        (1-(t/n))point + (t/n)*f(point) where t is the step in the function 
        after this function is completed, all the points will have their homotopy computed"""
        self.n_steps=n
        for line_index in range(len(self.lines)):
            self.lines[line_index].parameterize_points(function,n)
        self.pre_compute()#set the steps now so the program doesn't have to do this on the fly

         