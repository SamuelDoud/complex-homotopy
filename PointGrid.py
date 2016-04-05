import math
import cmath
import Line
import pickle
import function
from sympy import I, re, im, Abs, arg, conjugate, expand, Symbol, symbols
from sympy.abc import z


class PointGrid(object):
    """Point Grid holds all the points on the graph and their associations"""
    def __init__(self, corner_upper_left, corner_lower_right, n_lines):
        self.lines =[]
        self.n_steps = n_lines
        self.upper_left = corner_upper_left
        self.lower_right = corner_lower_right
        self.real_step = (self.lower_right.real - self.upper_left.real) / n_lines
        self.imaginary_step = (self.lower_right.imag - self.upper_left.imag) / n_lines
        self.z=symbols('z',complex=True)
        self.draw_lines()
        
    def draw_lines(self):
        self.draw_real()
        self.draw_imag()


    def draw_real(self):
        """Draw the lines with constant re(z)"""
        z=symbols('z',complex=True)
        upper = complex(self.upper_left.real-self.real_step,self.upper_left.imag)
        lower = complex(self.upper_left.real-self.real_step,self.lower_right.imag)
        for step in range(self.n_steps+2): #draw a line for the number of steps determined by the user            
            upper += complex(self.real_step,0)
            lower += complex(self.real_step,0)
            f_re_z = function.function(re(upper)+im(z)*I)#create a function (this may be improved if I can determine that adding x to f_re_z is possible)
            line = Line.Line(f_re_z,upper,lower,self.n_steps,self.n_steps,"blue") #create a line with starting points given
            self.add_line(line)

    def draw_imag(self):
        """Draw the lines with constant im(z)"""
        z=symbols('z',complex=True)
        upper = complex(self.upper_left.real,self.upper_left.imag-self.imaginary_step)
        lower = complex(self.lower_right.real,self.upper_left.imag-self.imaginary_step)
        for step in range(self.n_steps+2):
            upper += complex(0,self.imaginary_step)
            lower += complex(0,self.imaginary_step)
            f_im_z = function.function(re(z)+complex(0,(upper.imag)))
            line = Line.Line(f_im_z,upper,lower,self.n_steps,self.n_steps,"red")
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

    def provide_function(self,function,n):
        """Give a complex function to this function.
        Then, operate on each point by the function
        (1-(t/n))point + (t/n)*f(point) where t is the step in the function 
        after this function is completed, all the points will have their homotopy computed"""
        for line_index in range(len(self.lines)):
            self.lines[line_index].parameterize_points(function,n)

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
         