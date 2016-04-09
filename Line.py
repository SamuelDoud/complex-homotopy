﻿import numpy as np
import point

class Line(object):
    """Line is a container of points and delegates operations to them. Additionally, Line containss information shared among the points on a Line such as the color of the line, if it is connected, how many points are on the line etc.. Lines are held within a PointGrid"""

    def __init__(self, function, start, end,number_of_points, color,group, simply_connected=False,width=1):
        self.width=width
        self.simply_connected=simply_connected
        #self.name=name #the name of the Line,
        self.color=color #the color of this line
        self.function=function
        self.number_of_points=abs(number_of_points) #must be non-negative number of steps
        self.start=start
        self.end=end#the endpoints of this line
        self.points=self.create_points()
        self.group=group #shares the group varriable with other lines in this set. Made for deletion
        if self.simply_connected:
            self.points.append(self.points[0]) #this draws a line from the last point to the starting point...
            #needed if you draw a circle as there would not be a line connecting the two endpoints as they do not border eachother

    def create_points(self):
        z = self.start #this is the first value on the domain
        points = [point.point(self.function.evaluateAt(z))]#place tbe first element in the list
        step_length=(self.end - self.start)/self.number_of_points #the step length between points
        for step_index in range(self.number_of_points): #there is always at least a start and an end, start is already included, so end must be forced in
            z += step_length #move one step closer to the end of the domain
            f_z = self.function.evaluateAt(z) #evaluate the function at this complex number
            points.append(point.point(f_z)) #create a point located at
        return points

    def points_at_step(self,n):
        list_of_tuples=[pt.get_location_at_step(n) for pt in self.points] #get the location of every point at the n-th step
        return np.asarray(list_of_tuples).T.tolist()
    
    def parameterize_points(self,function,steps=None):
        """New function for the points on the line to draw to"""
        if not steps:
            steps=self.number_of_steps
        points=[]#temp list to store results
        for point in self.points:#take every point that has been defined by the create_points method
            f_z = function.evaluateAt(point.complex) #evaluate the function at this complex number
            point.parameterize(f_z,steps) #call on the point to parameterize itself given a new endpoint
            points.append(point) #throw that into a temp list
        self.points=points #reassign the old set of points to the temporary one. The temp list was used as the old points were being iterated over concurrently
        return points #hanf the points back to the caller for ease of use