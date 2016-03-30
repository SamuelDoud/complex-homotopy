from sympy import I, re, im, Abs, arg, conjugate, expand
import cmath
import point

class Line(object):
    """description of class"""
    def __init__(self, function,n, color, start, end, simply_connected=False):
        self.simply_connected=simply_connected
        self.name=name #the name of the Line,
        self.color=color #the color of this line
        self.function=function
        self.count=abs(n) #must be non-negative
        self.start=start
        self.end=end
        self.points=self.createPoints()
        
    def createPoints(self):
        z = self.start #this is the first value on the domain
        points = [z]
        step=(self.end - self.start)/self.count
        for step in range(self.count + 1): #there is always at least a start and an end, start is already included, so end must be forced in
            z += step #move one step closer to the end of the domain
            fz = self.function.evaluateAt(z)
            points.append(fz)
        return points 

    def NextFrame(self):
        """call for the next step in the deformation from each point contained on this line and send it up"""
        for i in range(len(self.points)):
            self.points.NextFrame()