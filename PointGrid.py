import math
import cmath
import Line
import pickle
import function
from sympy import I, re, im, Abs, arg, conjugate, expand, Symbol, symbols
from sympy.abc import z

REAL=0
IMAG=1 #constants for consistent iterable access
class PointGrid(object):
    """Point Grid holds all the points on the graph and their associations"""
    def __init__(self, corner_upper_left, corner_lower_right, n_lines, n_points):
        self.lines =[]
        self.n_lines = n_lines
        self.n_steps = 1
        self.n_points = n_points
        self.upper_left = corner_upper_left
        self.lower_right = corner_lower_right
        self.real_step = (self.lower_right.real - self.upper_left.real) / n_lines
        self.imaginary_step = (self.lower_right.imag - self.upper_left.imag) / n_lines
        self.z=symbols('z',complex=True)
        self.draw_lines()
        self.real_max=None
        self.real_min=None
        self.imag_max=None
        self.imag_min=None
        
    def draw_lines(self):
        self.draw_real()
        self.draw_imag()


    def draw_real(self):
        """Draw the lines with constant re(z)"""
        z=symbols('z',complex=True)
        upper = complex(self.upper_left.real,self.upper_left.imag)
        lower = complex(self.upper_left.real,self.lower_right.imag)#inital states of the lower and upper bound of the line
        for step in range(self.n_lines+1): #draw a line for the number of steps determined by the user            
            f_re_z = function.function(re(upper)+im(z)*I)#create a function (this may be improved if I can determine that adding x to f_re_z is possible)
            line = Line.Line(f_re_z,upper,lower,self.n_points,self.n_points,"blue") #create a line with starting points given
            self.add_line(line) #add the line to the list at large
            upper += complex(self.real_step,0)
            lower += complex(self.real_step,0) #shift the line on the real axis by real step

    def draw_imag(self):
        """Draw the lines with constant im(z)"""
        z=symbols('z',complex=True)
        upper = complex(self.upper_left.real,self.upper_left.imag)#the initial states of the upper and lower bounds of the line
        lower = complex(self.lower_right.real,self.upper_left.imag)
        for step in range(self.n_lines+1):
            f_im_z = function.function(re(z)+complex(0,(upper.imag)))
            line = Line.Line(f_im_z,upper,lower,self.n_points,self.n_points,"red")
            self.add_line(line)
            upper += complex(0,self.imaginary_step)
            lower += complex(0,self.imaginary_step) #shift the bounds by the imaginary step
   
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
        aligned_tuple=([],[])#tuple that will return all lines
        for line in self.lines:
            temp_tuple = line.points_at_step(n)
            aligned_tuple[REAL].append(temp_tuple[REAL])
            aligned_tuple[IMAG].append(temp_tuple[IMAG])
        return aligned_tuple

    def pre_compute(self):
        """Take every lines order and save it in an easily accessible list so computation doesn't have to be performed on the fly.
        Also, this function will track the min/max of both the real and imaginary axis"""
        self.computed_steps =[]
        self.real_min=self.lines[0].points[0].point_order[REAL][0]
        self.real_max=self.lines[0].points[0].point_order[REAL][0]
        self.imag_min=self.lines[0].points[0].point_order[IMAG][0]
        self.imag_max=self.lines[0].points[0].point_order[IMAG][0]
        for n in range(self.n_steps*2+2): #go through every step in the lines. n_steps * 2 because we are collecting the reversal steps too
            temp_tuple = self.lines_at_step(n)
            #algo to set min/max
            test_real_max = max(max(line) for line in temp_tuple[REAL])
            test_real_min = min(min(line) for line in temp_tuple[REAL])
            test_imag_min = min(min(line) for line in temp_tuple[IMAG])
            test_imag_max = max(max(line) for line in temp_tuple[IMAG])
            if self.real_max < test_real_max:
                self.real_max = test_real_max
            else:#if the max got set then there is no reason to test for the min
                if self.real_min > test_real_min:
                    self.real_min = test_real_min
            if self.imag_max < test_imag_max:
                self.imag_max = test_imag_max
            else:
                if self.imag_min > test_imag_min:
                    self.imag_min = test_imag_min
            self.computed_steps.append(temp_tuple)#add that tuple to the precomputed list
        pad=1.05
        self.force_square()
        #add 5% so the window isn't cramped. Now that I think about it.. there is a more pythonic way to do this
        self.real_max*=pad
        self.real_min*=pad
        self.imag_max*=pad
        self.imag_min*=pad
        return None
    def force_square(self):
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

    def create_animation(self, filename, function, number_of_steps, starting_lines=None, limits=(-10,10,-10,10)):
         """The creates a output of an animation based on the parameters provided.
         Write this information to a file"""
         if not starting_lines:
            self.lines=starting_lines #provides a new set of lines, if none are provided, use the old lines
         animation_data = [function,limits]
         
         self.provide_function(function, number_of_steps) #updates the points with the needed function and homotopy
         for line in self.lines:
            animation_data.append[line.info() + line.all_points_order()]#each line is a list of points which themselves are lists of their positions throughout the deformation
         data_to_save = {"function":function.text,"steps":number_of_steps, "limits":limits,"animated_lines":animation_data}
         pickle.dump(data_to_save, open(filename+"ch", "wb" ))#this serializes the data
         