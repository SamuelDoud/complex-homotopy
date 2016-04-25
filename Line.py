import cmath

import numpy as np

import ComplexPoint

PLUS = 0
MINUS = 1

class Line(object):
    """
    Line is a container of points and delegates operations to them. Additionally,
    Line contains information shared among the points on a Line such as the color
    of the line, if it is connected, how many points are on the line etc.. Lines
    are held within a PointGrid
    """
    def __init__(self, function, start, end, number_of_points, color, group,
                 simply_connected=False, width=1, points=None):
        self.singularity = []
        self.number_of_steps = 0
        self.width = width
        self.simply_connected = simply_connected
        #self.name=name #the name of the Line,
        self.color = color #the color of this line
        self.function = function
        #must be non-negative number of steps
        self.number_of_points = abs(number_of_points)
        self.start = start
        #the endpoints of this line
        self.end = end
        if points:
            self.points = points
        else:
            self.points = self.create_points()
        #shares the group varriable with other lines in this set. Made for deletion
        self.group = group
        if self.simply_connected:
            self.points.append(self.points[0])
            #This draws a line from the last point to the starting point.
            #Needed if you draw a circle as there would not be a line connecting the two endpoints
            #as they do not border eachother

    @classmethod
    def circle(cls, radius, center=complex(0, 0), points=100, color="black", group=0):
        """
        Alternative constructor for creating circle
        """
        thetas = np.linspace(0, 2 * np.pi, points)
        points = [ComplexPoint.ComplexPoint(cmath.rect(radius, theta) + center) for theta in thetas]
        return cls(0, 0, 0, 0, color, group, simply_connected=True, points=points)

    def create_points(self):
        """
        Taking a function, assign all z's on that line to a f(z)
        """
        #this is the first value on the domain
        zs_to_be_evaluated = np.linspace(self.start, self.end, self.number_of_points)
        return [ComplexPoint.ComplexPoint(f_z) for f_z in list(map(self.function.evaluate_at_point,
                                                     zs_to_be_evaluated))]

    def points_at_step(self, this_step, to_consider=False):
        """
        Get the points on this line at step n
        """
        #get the location of every point at the n-th step
        if not to_consider:
            list_of_tuples = [point.get_location_at_step(this_step) for point in self.points]
        else:
            list_of_tuples = [point.get_location_at_step(this_step) for point in self.points if not point.ignore_in_outliers]
        #take the list's transpose
        return np.asarray(list_of_tuples).T.tolist()

    def parameterize_points(self, function, steps=None):
        """
        New function for the points on the line to draw to
        """
        singularities = []
        if not steps:
            steps = self.number_of_steps
        else:
            self.number_of_steps = steps
        self.function = function
        #take every point that has been defined by the create_points method
        for index, pt_from_points in enumerate(self.points):
            try:
                #evaluate the function at this complex number
                f_z = self.function.evaluate_at_point(pt_from_points.complex)
                #call on the point to parameterize itself given a new endpoint
                pt_from_points.parameterize(f_z, steps)
                #call on the point to parameterize itself given a new endpoint
                self.points[index] = pt_from_points
            except ZeroDivisionError:
                #we should build points around an epsilon to provide better resolution!
                singularities.append((pt_from_points, index))
                #this point is a singularity and must be removed to allow the graph to operate
                print("A singularity at " + str(pt_from_points.complex) + ".")
        #remove the singularity points from the master list of points
        singularities.reverse()
        for point in singularities:
            self.points.pop(point[1])
        #deal with each singularity. Need to wait as the functionality adds points to the line
        for point in singularities:
            self.build_around(point)
        return singularities != []
        #we should add points to the line if we are operating on that list iteratively

    def build_around(self, singularity):
        """
        If a point is determined to be a singularity,
        create 24 points extremely close to that point.
        """
        #the index of the singularity we are currently working with.
        self.singularity_index = singularity[1]
        singularity_point = singularity[0].complex
        start = 5 #start close
        end = 3 #build outward from z
        samples = 12
        new_points = [(ComplexPoint.ComplexPoint(singularity_point + epsilon,
                                                 ignore_in_outliers=True),
                                                 ComplexPoint.ComplexPoint(singularity_point -
                                                 epsilon, ignore_in_outliers=True))
                      for epsilon in [complex(10 ** (-1 * power),10 ** (-1 * power)) for power in
                                    np.linspace(start, end, samples)]]
        map(self.inject_points, new_points)

    def inject_points(self, tuple_of_pm_epsilon):
        """
        Take the lines and inject them at the singuarity.
        Also, parameterize them
        To be used in conjuction with the map function in build_around.
        """
        plus_epsilon, minus_epsilon = tuple_of_pm_epsilon #tuple unpacking
        #parameterize the points
        plus_epsilon.parameterize(self.function.evaluate_at_point(plus_epsilon),
                                  self.number_of_steps)
        minus_epsilon.parameterize(self.function.evaluate_at_point(minus_epsilon),
                                   self.number_of_steps)
        self.points.insert(self.singularity_index, tuple_of_pm_epsilon[PLUS])
        self.points.insert(self.singularity_index, tuple_of_pm_epsilon[MINUS])
