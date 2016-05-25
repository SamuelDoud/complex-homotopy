import statistics

from sympy import re, im, arg, Abs, Symbol, symbols, I
import numpy as np

import Line
import ComplexFunction
import ComplexPoint

REAL = 0
IMAG = 1 #constants for consistent iterable access

class PointGrid(object):
    """
    Point Grid holds all the points on the graph and their associations
    """
    def __init__(self, limits=None, remove_outliers=True, lines=[]):
        """
        Create a point grid.
        """
        self.dpi = 100
        self.changed_flag_unhandled = False
        self.computed_steps_to_consider = None
        self.function = None
        self.computed_steps = []
        self.user_limits = limits
        self.remove_outliers = remove_outliers
        if self.user_limits:
            self.set_user_limits(self.user_limits)
        else:
            self.real_max = None
            self.real_min = None
            self.imag_max = None
            self.imag_min = None
        self.lines = lines
        self.n_steps = 1
        self.n_lines = 0
        self.complex_variable_symbol = symbols('z', complex=True)
        self.limit_mem = [None] * (self.n_steps + 2)
        self.filename = "z"
        self.functions = [ComplexFunction.ComplexFunction(self.filename)]

    def delete(self, group_number):
        """
        Remove every line in the list with a matching group number
        """
        for index, lines in enumerate(self.lines):
            if lines.group == group_number:
                #remove index from the list of lines
                self.lines.pop(index)
                #lower the count of lines by one
                self.n_lines -= 1

    def circle(self, radius, center=complex(0, 0), points=250):
        """
        Draws a circle of the given radius. User can set attributes such as center,
        the number of points, and the color of  the circle through kwargs.
        """
        #new group is being created
        return Line.Line.circle(radius, center, points)

    def grid_lines(self, complex_high_imag_low_real, complex_low_imag_high_real,
                   n_lines, n_points_per_line):
        """
        Create a grid with specified corners.
        Builds one continuous line of points in the form of a grid. There will be n_lines lines for
        each direction and each of these lines will have n_points_per_line points.
        """
        imag_diff = complex_high_imag_low_real.imag - complex_low_imag_high_real.imag
        real_diff = complex_low_imag_high_real.real - complex_high_imag_low_real.real
        #generate all the points on the edges.
        right_edge = np.linspace(complex(complex_low_imag_high_real.real,
                                    complex_high_imag_low_real.imag),
                            complex_low_imag_high_real, n_lines)
        left_edge =  np.linspace(complex_high_imag_low_real, complex(complex_high_imag_low_real.real,
                                                                complex_low_imag_high_real.imag),
                            n_lines)
        upper_edge = np.linspace(complex_high_imag_low_real,
                            complex(complex_low_imag_high_real.real,
                                    complex_high_imag_low_real.imag), n_lines)
        lower_edge = np.linspace(complex(complex_high_imag_low_real.real,
                                    complex_low_imag_high_real.imag),
                            complex_low_imag_high_real, n_lines)
        #the arrays that are used to draw to and from
        start = left_edge
        end = right_edge
        points = []
        for step in range(n_lines):
            points.extend(np.linspace(start[step], end[step], n_points_per_line).tolist())
            if step != n_lines - 1:
                points.append(end[step + 1])
                #swap start and end
                start, end = end, start
        #depending on if we ended on left or the right
        direction_to_use_list = range(n_lines)
        direction = 1
        if end is right_edge:
            #need to reverse the direction so we don't get a weird line in between these two loops
            list(direction_to_use_list).reverse()
            direction = -1
        start = lower_edge
        end = upper_edge
        if direction == -1:
            start = upper_edge
            end = lower_edge
        for step in direction_to_use_list:
            points.extend(np.linspace(start[step], end[step], n_points_per_line).tolist())
            #checking if on the last step
            if step != direction_to_use_list[-1]:
                points.append(end[step + direction])
                #swap start and end
                start, end = end, start
        #create a Line with the points generated
        point_objects = [ComplexPoint.ComplexPoint(point) for point in points]
        base_line = Line.Line('z', points[0], points[-1], len(points), point_objects)
        return base_line

    def disk(self, radius, num_circles, center, n_points_per_circle=250):
        """
        Build a disk centered at radius of num_circles density.
        """
        circles_as_lines = []
        radii_diff = radius / num_circles
        circles_as_points = [self.circle(radii_diff * (step + 1),
                               center, n_points_per_circle) for step in range(num_circles)]
        for circle_points in circles_as_points:
            temp_line = Line.Line('z', circle_points.points[0].complex,
                                  circle_points.points[-1].complex,
                                  len(circle_points.points), circle_points.points)
            temp_line.width = radii_diff * self.dpi
            circles_as_lines.append(temp_line)
        return circles_as_lines

    def add_line(self, line=None):
        """
        Add a line to the grid. This function tracks stats on this as well.
        """
        #could implement a sorting method here...
        #self.lines.sort(key=lambda key_value: key_value.name)
        if not line:
            self.lines = []
            self.n_lines = 0
            return
        self.lines.append(line)#add the new Line object to the list
        self.n_lines += 1 #a line has been added so the count is obviously greate

    def lines_at_step(self, this_step):
        """
        Get the state of every line at this current state
        """
        return [ln.points_at_step(this_step) for ln in self.lines]

    def lines_to_consider_at_step(self, this_step):
        """
        Get the points that don't have the marker on them..
        """
        return [ln.points_at_step(this_step, to_consider=True) for ln in self.lines]

    def lines_to_consider(self):
        """
        Gets all the points that do not have the ignore flag active.
        """
        self.computed_steps_to_consider = list(map(self.lines_to_consider_at_step,
                                                   range(self.n_steps)))

    def pre_compute(self):
        """
        Take every lines order and save it in an easily accessible list so computation
        doesn't have to be performed on the fly.
        Also, this function will track the min/max of both the real and imaginary axis
        """
        #Get every step in this homotopy and map it to this list.
        self.computed_steps = list(map(self.lines_at_step, range(self.n_steps)))
        #set the limits of the graph based upon the computation
        self.set_limits()

    def set_user_limits(self, limits_tuple):
        """
        Pass a tuple of (real max, real min, imag max, and imag min) to set your own limits
        """
        #tuple unpacking
        if None in limits_tuple:
            #forcing to None allows for the user to go back to auto limits
            self.user_limits = None
        else:
            #set the limits manually and store in a tuple
            self.real_max, self.real_min, self.imag_max, self.imag_min = limits_tuple
            self.user_limits = (self.real_max, self.real_min, self.imag_max, self.imag_min)

    def set_limits(self):
        """
        Calls on the PointGrid to create a set of limits or defer to the user's judgement.
        """
        #the user has specified their own limits. These limits take prrecedence
        if self.user_limits:
            return
        if not self.computed_steps_to_consider:
            lines = self.computed_steps
        else:
            lines = self.computed_steps_to_consider
        #flatten the list
        flattened_steps = [item for sublist in lines for item in sublist]
        #Credit to Stack Overflow user Alex Martelli
        #stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        complex_flattened_steps = list(zip(*flattened_steps))
        reals = []
        imags = []
        if flattened_steps:
            #check that we don't have an empty list
            [reals.extend(line) for line in complex_flattened_steps[REAL]]
            [imags.extend(line) for line in complex_flattened_steps[IMAG]]
            self.set_limits_agnostic(reals, imags)

    def limits_at_step(self, step):
        """
        The user has elected to set the limits based the current display
        """
        if not self.limit_mem[step % self.n_steps]:
            current_points = list(zip(*self.lines_at_step(step)))
            self.set_limits_agnostic(current_points[REAL][0],
                                     current_points[IMAG][0])
            self.limit_mem[step] = ((self.real_max, self.real_min,
                                     self.imag_max, self.imag_min))
        else:
            #tuple unpacking from memory as this limit has already been determined
            (self.real_max, self.real_min,
             self.imag_max, self.imag_min) = self.limit_mem[step % self.n_steps]

    def set_limits_agnostic(self, reals, imags):
        """
        This function will set the limits based on the point data passed to it.
        Works for both the limits_at_step and overall set_limits
        """
        #if this feature is active, then outliers will be removed
        if self.remove_outliers:
            reals = remove_outliers_operation(reals)
            imags = remove_outliers_operation(imags)
        #add 5% so the window isn't cramped.
        pad = 1.05
        self.real_max = max(reals) * pad
        self.real_min = min(reals) * pad
        self.imag_max = max(imags) * pad
        self.imag_min = min(imags) * pad
        #make the limits square so the graph isn't distorted
        self.force_square()

    def force_square(self):
        """
        Force the min-maxes to form a square.
        """
        real_diff = self.real_max - self.real_min
        imag_diff = self.imag_max - self.imag_min
        if real_diff > imag_diff:
            self.imag_max += ((real_diff - imag_diff) / 2)
            self.imag_min -= ((real_diff-imag_diff) / 2)
        else:
            self.real_max += ((imag_diff-real_diff) / 2)
            self.real_min -= ((imag_diff-real_diff) / 2)

    def pre_computed_steps(self, this_step):
        """
        Get the precomputed step n. Contains a modulo to prevent overflow
        """
        return self.computed_steps[this_step % (self.n_steps)]

    def new_lines(self, lines_to_add=None):
        """
        Remove lines from the Point Grid
        """
        if lines_to_add:
            self.lines = lines_to_add
            self.lines += 1
            #adding sequentally protects
            #self.pre_compute()
        else:
            self.lines = []
            self.n_lines = 0
        #self.changed_flag_unhandled = True

    def provide_function(self, functions, number_of_steps_to_compute,
                         collection_of_lines, reverse=False):
        """Give a complex function to this function.
        Then, operate on each point by the function
        (1-(t/n))point + (t/n)*f(point) where t is the step in the function
        after this function is completed, all the points will have their homotopy computed"""
        self.lines = collection_of_lines
        lines_to_readd = []
        self.new_lines()

        #cull the lines to remove duplicates
        culled_and_flattened_lines = flattened_lines(collection_of_lines)
        if self.functions == functions or self.n_steps == number_of_steps_to_compute:
            #the function is the same as the last run. Truncate the list of lines so that only unique lines are included
            for line in culled_and_flattened_lines:
                if Line.compare(line, self.lines):
                    #this line was already computed, don't recompute it
                    culled_and_flattened_lines.remove(line)
        if self.functions != functions:
            #we have a new set of functions, no tricks can be used to avoid computation
            self.functions = functions
            #get the total filename of the function
            #start with the first function
            self.filename = self.functions[0].filename
            #then go through the rest
            if len(self.functions) > 1:
                for function in self.functions[1:]:
                    self.filename = self.filename + ";" + function.filename

        #remove all lines
        self.add_line()
        #readd the lines to compute
        for line in culled_and_flattened_lines:
            self.add_line(line)

        #delete these lines. Their existence determines actions
        self.computed_steps_to_consider = []
        #wipe the memory of the limits and creates a list of size n_steps
        self.limit_mem = [None] * (self.n_steps)
        singularity = []
        for line_index in range(self.n_lines):
            singularity.append(self.lines[line_index].parameterize_points(functions,
                                                                        number_of_steps_to_compute,
                                                                        reverse=reverse))
        #set the steps now so the program doesn't have to do this on the fly
        #this is actually taking the number of steps at the first point on the first line only
        #assuming that this is going to be consistent throughout the plane
        try:
            self.n_steps = self.lines[0].number_of_steps
        except IndexError:
            self.n_steps = 1
        #if a singularity exists, set the lines to consider limit
        if any(singularity):
            self.lines_to_consider()
        #readd the lines that we determined didn't need to be computed
        for line in lines_to_readd:
            self.add_line(line)
        self.pre_compute()

def remove_outliers_operation(points, z_limit=3):
    """
    This removes outliers from the setting of limits.
    Default to z = 3. Equivalent to three standard deviations from
    the median(!). Median is specifically used in this situation as
    the mean can be a poor measure when a point could lie at near infinity.
    """
    low = 0
    high = 1
    st_dev = statistics.stdev(points)
    median = statistics.median(points)
    #define an outlier as any point +/-z*st_dev off the median
    #must lie within range in order to not be an outlier
    limits = (median - st_dev*z_limit, median + st_dev*z_limit)
    return [pt for pt in points if pt >= limits[low] and pt <= limits[high]]


def distance(start, end):
    return ((start.real - end.real)**2 + (start.imag - end.imag)**2)**0.5

def flattened_lines(line_collection):
    """
    The collection of lines is a list of tuples with
    each tuple containing a list of lines and an id.
    This method takes all the lines in the collection
    and returns them as one list.
    """

    stripped_of_id = [line[0] for line in line_collection]
    return [item for sublist in stripped_of_id for item in sublist]
