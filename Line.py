import cmath

import numpy as np

import point

PLUS=0
MINUS=1

class Line(object):
    """Line is a container of points and delegates operations to them. Additionally, Line containss information shared among the points on a Line such as the color of the line, if it is connected, how many points are on the line etc.. Lines are held within a PointGrid"""

    def __init__(self, function, start, end,number_of_points, color,group, simply_connected=False,width=1,points=None):
        self.width=width
        self.simply_connected=simply_connected
        #self.name=name #the name of the Line,
        self.color=color #the color of this line
        self.function=function
        self.number_of_points=abs(number_of_points) #must be non-negative number of steps
        self.start=start
        self.end=end#the endpoints of this line
        if points:
            self.points=points
        else:
            self.points=self.create_points()
        self.group=group #shares the group varriable with other lines in this set. Made for deletion
        if self.simply_connected:
            self.points.append(self.points[0]) #this draws a line from the last point to the starting point...
            #needed if you draw a circle as there would not be a line connecting the two endpoints as they do not border eachother

    @classmethod
    def circle(cls,radius, center=complex(0,0), points=100,color="black",group=0):
        """
        Alternative constructor for creating circle
        """
        thetas=np.linspace(0,2*np.pi,points)
        points=[point.point(cmath.rect(radius,theta)+center) for theta in thetas]
        return cls(0,0,0,0,color,group,simply_connected=True,points=points)

    def create_points(self):
        """
        Taking a function, assign all z's on that line to a f(z)
        """
        zs = np.linspace(self.start,self.end,self.number_of_points) #this is the first value on the domain
        return [point.point(f_z) for f_z in list(map(self.function.evaluateAt, zs))]



    def points_at_step(self,n):
        list_of_tuples=[pt.get_location_at_step(n) for pt in self.points] #get the location of every point at the n-th step
        return np.asarray(list_of_tuples).T.tolist() #take the list's transpose
    
    def parameterize_points(self,function,steps=None):
        """New function for the points on the line to draw to"""
        singularities = []
        if not steps:
            steps=self.number_of_steps
        else:
            self.number_of_steps=steps
        self.function=function
        for index, pt in enumerate(self.points):#take every point that has been defined by the create_points method
            try:
                f_z = self.function.evaluateAt(pt.complex) #evaluate the function at this complex number
                pt.parameterize(f_z,steps) #call on the point to parameterize itself given a new endpoint
                self.points[index]=pt #throw that into a temp list
            except ZeroDivisionError:
                #we should build points around an epsilon to provide better resolution!
                singularities.append(pt)
                self.points.remove(pt) #this point is a singularity and must be removed to allow the graph to operate
                print("A singularity at " + str(pt.complex) + ".")
        map(self.build_around, singularities) #deal with each singularity. Need to wait as the functionality adds points to the line
        return singularities is not None
        #we should add points to the line if we are operating on that list iteratively

    def build_around(self,z,index):
        self.singularity=index #the index of the singularity we are currently working with. need
        start=5 #start close
        end=3 #build outward from z
        samples=12
        new_points=[(point.point(z + epsilon), point.point(z - epsilon)) for epsilon in [10**(-1 * power) for power in np.linspace(start,end,samples)]]
        map(inject_points, new_points)
        self.points.sort()
        
    def inject_points(self,tuple_of_pm_epsilon,):
        """
        Take the lines and inject them at the singuarity.
        Also, parameterize them
        To be used in conjuction with the map function in build_around.
        """
        plus_epsilon, minus_epsilon = tuple_of_pm_epsilon #tuple unpacking
        #parameterize the points
        plus_epsilon.parameterize(self.function.evaluateAt(plus_epsilon),self.number_of_steps)
        minus_epsilon.parameterize(self.function.evaluateAt(minus_epsilon),self.number_of_steps)
        self.points.insert(self.singularity+1,tuple_of_pm_epsilon[PLUS])
        self.points.insert(self.singularity,tuple_of_pm_epsilon[MINUS])