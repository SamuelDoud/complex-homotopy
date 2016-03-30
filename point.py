import cmath
from sympy import I, re, im, Abs, arg, conjugate, expand

class point(object):
    """This class defines a point on a graph and the order in which those points are displayed.
    User must pass a real and imaginary starting position to the point object"""
    def __init__(self, real, imag, function=None, n=1):
        self.real = real
        self.imag = imag
        self.f_real = f_real
        self.f_imag = f_imag
        self.increment = 1 #init value for the incrementation (1 is for z to f(z), -1 is for f(z) to z)
        self.point_order = [(real, imag)]
        self.counter = 0
        self.n=n
        self.function = function
        if not self.function:
            self.updatePoint(self.function, self.n)#a function was provided, calculate the homotopy
    def setPoints(self, list_points):
        """given a new set of points, update this point's points and reset the n and counter"""
        self.point_order=list_points
        self.n = len(self.point_order) #set n to zero to bring the animation back to the base state
        self.counter = 0 # reset the counter

    def get_point(self):
        """this would be naive, however n must be incremented so the next call actually returns a new point (may have to reset the graph!). so it is done verbosely"""
        if counter % n == 0: #whenever counter is at a multiple of n, we are at the end of a cycle
            self.increment*=-1 #this maps 1 to -1 and -1 to 1, reversing the animation
        n+=increment #actually do the incremntation
        #this configuration has the homotopy running in reverse!
        #so if counter is equal to 0, set the increment to 1
        #when the counter reaches n, set the increment to -1 
        return self.point_order[n] #return the current points in the animation process.

    def updatePoint(self, function, desired_steps):
        """given a function and a desired numbers of steps, update this point in the grid to match that"""
        list_points=[]
        self.function = function
        result_at_point = self.function.evaluateAt(complex(self.real, self.imag)) #get the result of f(z)
        self.f_real = re(result_at_point)
        self.f_imag = im(result_at_point) #these are the final points in the homotopy
        for step in range(desired_steps):
            t = step / (desired_steps+0.0)
            less_t = (1-t) #tracking of progress variables, this is not needed to be written explictly
            list_points.append((less_t*real + t*f_real, less_t*imag + t*f_imag)) #add to the list as a tuple
        self.setPoints(list_points) #update the points as specified
