from sympy import I, re, im, Abs, arg, conjugate, expand
import cmath
import point

class Line(object):
    """Line is a container of points and delegates operations to them. Additionally, Line containss information shared among the points on a Line such as the color of the line, if it is connected, how many points are on the line etc.. Lines are held within a PointGrid"""
    def __init__(self, function,number_of_points, number_of_steps, color, start, end, simply_connected=False):
        self.simply_connected=simply_connected
        self.name=name #the name of the Line,
        self.color=color #the color of this line
        self.function=function
        self.number_of_points=abs(number_of_points) #must be non-negative number of steps
        self.number_of_steps=number_of_steps
        self.start=start
        self.end=end#the endpoints of this line
        self.points=self.createPoints()
        if self.simply_connected:
            self.points.append(self.points[0]) #this draws a line from the last point to the starting point...
            #needed if you draw a circle as there would not be a line connecting the two endpoints as they do not border eachother
        
    def create_points(self):
        z = self.start #this is the first value on the domain
        points = [z]
        step_length=(self.end - self.start)/self.number_of_points #the step length between points
        for step_index in range(self.count + 1): #there is always at least a start and an end, start is already included, so end must be forced in
            z += step_length #move one step closer to the end of the domain
            fz = self.function.evaluateAt(z) #evaluate the function at this complex number
            temp_point = point(re(fz), im(fz),n=self.number_of_steps) #create a point located at 
            points.append(temp_point) 
        return points

    def next_frame(self):
        """call for the next step in the deformation from each point contained on this line and send it up"""
        for i in range(len(self.points)):
            self.points.NextFrame()

    def new_function(self, function, n=0):
        """Issue a new function to the points. This function is independent of the line's initial construction!
        This function is the function that describes the animation of the points"""
        for i in range(len(points)):
            points[i].set_function(function, n)