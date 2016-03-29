import cmath
class point(object):
    """This class defines a point on a graph and the order in which those points are displayed.
    User must pass a real and imaginary starting position to the point object"""
    def __init__(self, real, imag, f_real=None, f_imag=None, n=1):
        self.real = real
        self.imag = imag
        self.f_real = f_real
        self.f_imag = f_imag
        self.increment = 1 #init value for the incrementation
        self.point_order = [(real, imaginary)]
        self.counter = 0
    def setPoints(self, list_points):
        """given a new set of points, update this point's points and reset the n and counter"""
        self.point_order=list_points
        self.n = len(self.point_order) #set n to zero to bring the animation back to the base state
        self.counter = 0 # reset the counter
    def get_point(self):
        """this would be naive, however n must be incremented so the next call actually returns a new point (may have to reset the graph!). so it is done verbosely"""
        new_point = self.point_order[n]
        if counter is n:
            self.increment = -1
        if counter is 0:
            self.increment = 1
        n+=increment
        #possibly allow this to run in reverse by having a secondary bit of logic
        #so if counter is equal to 0, set the increment to 1
        #when the counter reaches n, set the increment to -1    
        return new_point

    def updatePoint(self, function, z, desired_steps):
        """given a function and a desired numbers of steps, update this point in the grid to match that"""
        list_points=[]
        magical_function_evaluation_complex=complex() #evaluate the function... TODO
        f_real = magical_function_evaluation_complex.real
        f_imag = magical_function_evaluation_complex.imag
        for step in range(desired_steps):
            t = step / (desired_steps+0.0)
            less_t = (1-t) #tracking of progress variables, this is not needed to be written explictly
            list_points.append((less_t*real + t*f_real, less_t*imag + t*f_imag)) #add to the list as a tuple
        self.setPoints(list_points) #update the points as specified
