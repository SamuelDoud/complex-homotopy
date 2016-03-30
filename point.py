import cmath
from sympy import I, re, im, Abs, arg, conjugate, expand

class point(object):
    """This class defines a point on a graph and the order in which those points are displayed.
    User must pass a real and imaginary starting position to the point object"""
    def __init__(self, real, imag, function=None, n=1):
        self.real = real
        self.imag = imag
        self.point_order = [(real, imag)]
        self.counter = 0
        self.n=n
        self.function = function
        if not self.function:
            self.updatePoint(self.function, self.n)#a function was provided, calculate the homotopy

    def set_function(function, n=0):
        """Adds a new function to this point"""
        if n is not 0:
            self.n=n
        self.reset() #reset the counter and increment for this point
        self.function=function
        self.update_point(self.function, self.n)

    def set_points(self, list_points):
        """given a new set of points, update this point's points and reset the n and counter"""
        self.point_order=list_points
        self.n = len(self.point_order) #set n to zero to bring the animation back to the base state
        self.counter = 0 # reset the counter

    def update_point(self, function, desired_steps):
        """given a function and a desired numbers of steps, update this point in the grid to match that"""
        list_points=[]
        self.function = function
        result_at_point = self.function.evaluateAt(complex(self.real, self.imag)) #get the result of f(z)
        self.f_real = re(result_at_point)
        self.f_imag = im(result_at_point) #these are the final points in the homotopy
        for step in range(desired_steps + 1): #creates desired_steps anamations from the state z to the state f(z)
            t = step / (desired_steps+0.0)
            less_t = (1-t) #tracking of progress variables, this is not needed to be written explictly
            list_points.append((less_t*real + t*f_real, less_t*imag + t*f_imag)) #add to the list as a tuple
        self.set_points(list_points) #update the points as specified
