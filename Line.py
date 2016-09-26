import cmath

import numpy as np

import ComplexPoint

PLUS = 0
MINUS = 1

REAL = 0
IMAG = 1

class Line(object):
    """
    Line is a container of points and delegates operations to them. Additionally,
    Line contains information shared among the points on a Line such as the color
    of the line, if it is connected, how many points are on the line etc.. Lines
    are held within a PointGrid
    """
    def __init__(self, function, start, end, number_of_points,
                 points=None, start_color=None, end_color=None, optimize=True):
        self.singularity = []
        self.optimize = optimize
        self.singularity_index = -1
        self.number_of_steps = 0
        self.width = 1
        self.dash_seq = None
        self.computed = False
        self.function = function
        self.reals = []
        self.imaginaries = []
        #must be non-negative number of steps
        self.number_of_points = number_of_points
        self.start = start
        #the endpoints of this line
        self.end = end
        if start_color and end_color:
            self.start_color = start_color
            self.end_color = end_color
        else:
            self.start_color = (0, 0, 0)
            self.end_color = (0, 0, 0)
        if not points:
            self.create_points()
        else:
            self.points = points
        self.create_op_points()

    @classmethod
    def circle(cls, radius, center=complex(0, 0), points=100, start_color=None, end_color=None):
        """Alternative constructor for creating circle"""
        thetas = np.linspace(0, 2 * np.pi, points)
        points = [ComplexPoint.ComplexPoint(cmath.rect(radius, theta) + center) for theta in thetas]
        #circles and other simply connected objects need this in order to be a closed set
        #must create a new point instead of attaching the head to the tail.
        #if that is done then the functions will evaluate twice over this point
        points.append(ComplexPoint.ComplexPoint(points[0].complex))
        return cls(0, 0, 0, 0, points, start_color=start_color, end_color=end_color, optimize=False)

    def create_points(self):
        """
        Taking a function, assign all z's on that line to a f(z)
        """
        #this is the first value on the domain
        zs_to_be_evaluated = np.linspace(self.start, self.end, self.number_of_points)
        self.points = [ComplexPoint.ComplexPoint(f_z) for f_z in zs_to_be_evaluated]

    def points_at_step(self, this_step, n_steps, to_consider=False):
        """
        Get the points on this line at step n
        """
        #get the location of every point at the n-th step
        if not to_consider:
            list_of_tuples = [point.get_location_at_step(this_step)
                              for point in self.points]
        else:
            list_of_tuples = [point.get_location_at_step(this_step)
                              for point in self.points if not point.ignore_in_outliers]
        #break into real and imag lists
        color_diff = tuple(((self.end_color[color_index] - self.start_color[color_index]) / n_steps) for color_index in range(3))
        colors = []
        if n_steps > 1:
            for index, color in enumerate(color_diff):
                colors.append(color * (this_step % (n_steps - 1)) + self.start_color[index])
        else:
            colors = list(self.start_color)
        split_list = list(zip(*list_of_tuples)) + [colors]
        return split_list

    def parameterize_points(self, functions, steps=None, reverse=False):
        """
        New function for the points on the line to draw to
        """
        do_append = False
        if not steps:
            #don't change the number of steps
            steps = self.number_of_steps
        else:
            self.number_of_steps = steps
        for function in functions:
            #going through each function in the list of functions
            singularities = []
            #take every point that has been defined by the create_points method
            for index, pt_from_points in enumerate(self.points):
                try:
                    #evaluate the function at this complex number
                    if do_append:
                        #take the last point in the point order
                        last = pt_from_points.point_order[-1]
                        #eval the funct w/ the last point in the point order as a complex number
                        f_z = function.evaluate_at_point(complex(last[ComplexPoint.REAL],
                                                                 last[ComplexPoint.IMAG]))
                    else:
                        f_z = function.evaluate_at_point(pt_from_points.complex)
                    #call on the point to parameterize itself given a new endpoint
                    pt_from_points.parameterize(f_z, steps, append=do_append)
                    #call on the point to parameterize itself given a new endpoint
                except ZeroDivisionError:
                    #we should build points around an epsilon to provide better resolution!
                    singularities.append((pt_from_points, index))
                    #this point is a singularity and must be removed to allow the graph to operate
                    print("A singularity at " + str(pt_from_points.complex) + ".")
            #remove the singularity points from the master list of points
            singularities.reverse()
            for point in singularities:
                self.points.remove(point)
            #deal with each singularity. Need to wait as the functionality adds points to the line
            for point in singularities:
                self.build_around(point)
            if singularities:
                self.create_op_points
                self.parameterize_points(functions, steps=steps, reverse=reverse)
            #now move on to append
            do_append = True
        #the user wants to reverse the function
        if reverse:
            for point in self.points:
                point.add_reverse_to_point_order()
        #take the length of the point order of the first point
        self.computed = True
        self.set_points()

    def set_points(self):
        self.reals = []
        self.imaginaries = []
        for point in self.points:
            pt_order_split = list(zip(*point.point_order))
            self.reals.extend(pt_order_split[REAL])
            self.imaginaries.extend(pt_order_split[IMAG])


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
                                                 True),
                       ComplexPoint.ComplexPoint(singularity_point - epsilon, True))
                      for epsilon in [complex(10 ** (-1 * power), 10 ** (-1 * power)) for power in
                                      np.linspace(start, end, samples)]]
        #take every poin and use the inject points method on it
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

    def create_op_points(self):
        """Create a list of points that only contains unique points by referencing unique
        memory addresses for same base points."""
        if not self.optimize:
            return
        all_points = [point.complex for point in self.points]
        seen_points = {}
        for index, point in enumerate(all_points):
            seen_points[point] = index
        ref_to_index = [seen_points[z] for z in all_points]
        temp_points = [self.points[index] for index in ref_to_index]
        self.points = temp_points


def compare(master, child_lines):
    """Check if master and child have the same points"""
    master_start_points = [complex_point.complex for complex_point in master.points]
    child_start_points = [[(complex_point.complex
                            for complex_point in child.points)] for child in child_lines]
    return master_start_points in child_start_points
