import statistics
import math

from sympy import re, im, arg, Abs, Symbol, symbols, I
import numpy as np

import Line
import ComplexFunction
import ComplexPoint

REAL = 0
IMAG = 1 #constants for consistent iterable access

LINE_INDEX = 0

#this establishes an identity ffunction for external clases to use
identity_function = ComplexFunction.ComplexFunction("z")


class PointGrid(object):
    """
    Point Grid holds all the points on the graph and their associations
    """
    def __init__(self, limits=None, remove_outliers=True, lines=None):
        """
        Create a point grid.
        """
        self.dpi = 100
        self.changed_flag_unhandled = False
        self.computed_steps_to_consider = None
        self.function = None
        self.reverse = False
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
        if lines:
            self.lines = lines
        else:
            self.lines = []
        self.flattened_lines_cache = None
        self.n_steps = 1
        self.n_lines = 0
        self.complex_variable_symbol = symbols('z', complex=True)
        self.limit_mem = [None] * (self.n_steps + 2)
        self.filename = "z"
        self.functions = None

    def delete(self, line):
        """
        Remove every line in the list with a matching group number
        """
        #remove index from the list of lines
        if isinstance(line, list):
            line = line[0]
        try:
            index = self.lines.index(line)

        except ValueError:
            return
        for step in self.computed_steps:
            step.pop(index)
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

    def draw_line(self, complex_start, complex_end, points=50):
        """
        Draw a "line" on the complex plane between two complex numbers.
        This is a interface to the Line class
        """
        return Line.Line(identity_function, complex_start, complex_end, points)
        pass

    def draw_roots_of_unity_spindle(self, n_roots, n_circles, total_radius=1, center = complex(0,0)):
        """
        Draw the lines that form a circle that is has the roots of unity on its radius foorming lines to its center.
        """
        radius_diff = total_radius / n_circles
        circles_on_the_spindle = []
        roots_of_unity_lines = []
        [circles_on_the_spindle.append(self.circle(n * radius_diff, center)) for n in range(1, n_circles + 1)]
        #take the roots of unity and move them by what was passed as the center
        #this is only going to work if the circle has radius 1
        roots_of_unity_endpoints = offset_by(roots_of_unity(n_roots), center)
        #draw the lines that form the roots of unity
        for root_point in roots_of_unity_endpoints:
            roots_of_unity_lines.append(self.draw_line(center, root_point))
        return flatten_spindle(roots_of_unity_lines, circles_on_the_spindle, center, total_radius)
    
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
        left_edge = np.linspace(complex_high_imag_low_real,
                                complex(complex_high_imag_low_real.real,
                                        complex_low_imag_high_real.imag), n_lines)
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

    def build_line(self, start, end, n_points=50, color=None):
        """Build a straight line on the complex plane."""
        points_on_line = np.linspace(start, end, n_points)
        line = Line.Line("z", points_on_line[0], points_on_line[-1], n_points, color=color)
        return line

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
            #temp_line.width =  self.dpi
            circles_as_lines.append(temp_line)
        return circles_as_lines

    def add_line(self, line, index=-1):
        """
        Add a line to the grid. This function tracks stats on this as well.
        """
        #could implement a sorting method here...
        #self.lines.sort(key=lambda key_value: key_value.name)
        #delete all lines if no lines are passed
        #add the line and increase teh n_lines counter
        if index >= 0:
            self.lines.insert(index, line)
        else:
            self.lines.append(line)
        self.n_lines += 1

    def lines_at_step(self, this_step):
        """
        Get the state of every line at this current state
        """
        return [ln[0].points_at_step(this_step) for ln in self.lines]

    def lines_to_consider_at_step(self, this_step):
        """
        Get the points that don't have the marker on them..
        """
        return [ln[0].points_at_step(this_step, to_consider=True) for ln in self.lines]

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
        reals = []
        imaginaries = []
        for line_tuple in self.lines:
            line_object = line_in_tuple(line_tuple)
            reals.extend(line_object.reals)
            imaginaries.extend(line_object.imaginaries)
        self.set_limits_agnostic(reals, imaginaries)

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
        if not reals or not imags:
            reals = [0]
            imags = [0]
        self.real_max = max(reals)
        self.real_min = min(reals)
        self.imag_max = max(imags)
        self.imag_min = min(imags)
        #make the limits square so the graph isn't distorted
        self.force_square()

    def force_square(self):
        """
        Force the min-maxes to form a square.
        """
        #how much space will the objects be from the edge of the graph
        pad = 1.05
        real_diff = (self.real_max - self.real_min)
        imag_diff = (self.imag_max - self.imag_min)
        #big change is how much the axis w/ the smaller difference will need to change by
        big_change = math.fabs((real_diff - imag_diff) / 2) * (pad / 2)
        #this is the distance the smaller axis will change by
        little_change = (pad - 1) / 2
        if real_diff > imag_diff:
            little_change *= real_diff
            self.real_max += little_change
            self.real_min -= little_change
            self.imag_max += big_change + little_change
            self.imag_min -= big_change + little_change
        else:
            little_change *= imag_diff
            self.imag_max += little_change
            self.imag_min -= little_change
            self.real_max += big_change + little_change
            self.real_min -= big_change + little_change

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
            self.n_lines = len(lines_to_add)
        else:
            self.lines = []
            self.n_lines = 0


    def provide_function(self, functions, number_of_steps_to_compute, reverse=False, limits=None,
                         remove_outliers=False):
        """Give a complex function to this function.
        Then, operate on each point by the function
        (1-(t/n))point + (t/n)*f(point) where t is the step in the function
        after this function is completed, all the points will have their homotopy computed"""
        self.remove_outliers = remove_outliers
        sigularities = []
        if (functions == self.functions and number_of_steps_to_compute == self.n_steps and
        reverse == self.reverse):
            lines_to_compute = []
            #find the lines without computations
            for line_tuple in self.lines:
                line = line_in_tuple(line_tuple)
                if not line.computed:
                    #add to the will-compute list
                    lines_to_compute.append(line_tuple)
        else:
            lines_to_compute = self.lines
            if self.functions != functions:
                self.functions = functions
                self.set_filename(functions)
        self.n_steps = (number_of_steps_to_compute - 1) * len(functions) + 1
        self.reverse = reverse
        if reverse:
            self.n_steps *= 2
        for line_tuple in lines_to_compute:
            line = line_in_tuple(line_tuple)
            sigularities.append(line.parameterize_points(self.functions,
                                                         number_of_steps_to_compute, reverse))
        self.pre_compute()
        if limits:
            #the user has defined their own limits
            self.user_limits = limits
            self.set_user_limits(self.user_limits)
        else:
            self.set_limits()

    def set_filename(self, functions):
        """Set the filename given a set of functions"""
        #get the first functions filename
        self.filename = functions[0].filename
        #then go through the rest
        if len(functions) > 1:
            for function in functions[1:]:
                self.filename = self.filename + ";" + function.filename

def roots_of_unity(n_roots):
    """
    Takes the roots of unity for the passed variable n_roots.
    """
    list_of_roots = []
    pi = math.pi
    for nth_root in range(n_roots):
        list_of_roots.append(cis((2 * nth_root * pi) / n_roots))
    return list_of_roots

def cis(argument):
    """
    DRY mandated function for the common complex function of "cos(z) + i * sin(z)" in a function.
    """
    return math.cos(argument) + complex(0, 1) * math.sin(argument) 

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
    """Get the distance between two complex points"""
    return ((start.real - end.real)**2 + (start.imag - end.imag)**2)**0.5

def flatten_lines(line_collection):
    """
    The collection of lines is a list of tuples with
    each tuple containing a list of lines and an id.
    This method takes all the lines in the collection
    and returns them as one list.
    """
    stripped_of_id = [line[0] for line in line_collection]
    return [item for sublist in stripped_of_id for item in sublist]

def line_in_tuple(line_tuple):
    return line_tuple[0]

def list_set_minus(big_list, little_list):
    """Return the elements of big_list not in small list"""
    return list(set(big_list) - set(little_list))

def list_set_intersection(big_list, little_list):
    """Return the elements of big_list in small list"""
    return list(set(big_list).intersection(set(little_list)))

def offset_by(list_of_points, center):
    if isinstance(list_of_points, list):
        for point in list_of_points:
            point = point + center
    else:
        for point in list_of_points.points:
            point.complex = point.complex + center
    return list_of_points

def flatten_spindle(lines, circles, center, radius):
    """passed a list of lines and circles, combine them into a single line
    normalize to the lines and circles to (0,0)"""
    n_circles = len(circles)
    radius_diff = radius / n_circles
    lines = [offset_by(line, -1 * center) for line in lines]
    circles = [offset_by(circle, -1 * center) for circle in circles]
    #outermost circle
    master_circle = circles[-1]
    #all the other circles
    slave_circles = circles[:-1]
    unified_lines = []
    #empty checks
    if(len(lines) < 1 or len(circles) < 1):
        return []
    #take a "master line" the circle and the rest of the lines 
    master_line = lines[0]
    master_line_len = len(master_line.points)
    run = (master_line.points[-1 ].complex.real - master_line.points[0].complex.real)
    #do not allow zero values
    run = (run if run != 0 else 0.000001)
    rise = (master_line.points[-1 ].complex.imag - master_line.points[0].complex.imag)
    master_line_slope = rise / run
    #find where the circle intersects with the master line
    min_distance = (rise**2 + run **2)**0.5
    min_distance_index = 0
    #gets the smallest distance between the line and the outer circle
    for index, point in enumerate(master_circle.points):
        distance_between_circle_and_line = distance(master_line.points[-1].complex, point.complex)
        if (distance_between_circle_and_line < min_distance):
            min_dist = distance_between_circle_and_line
            min_distance_index = index
    #add the point with the smallest distance to the circle
    master_circle.points.insert(min_distance_index, master_line.points[-1])
    master_line.points.extend(master_circle.points)
    if slave_circles:
        for index, slave_circle in enumerate(reversed(slave_circles)):
            insertion_point = int(((len(slave_circles) - index) * master_line_len) / len(circles))
            master_line.points.insert(insertion_point, slave_circle.points[min_distance_index])
            master_line.points[insertion_point:insertion_point] = slave_circle.points
    if (len(lines) > 1):
        slave_lines = lines[1:]
        #connect the master line to its slaves
        #the best way to do this is probably connecting on the master_circle (the outermost circle)
        #this algo is much, much simpler though. There is value in that.
        slave_line_len = len(slave_lines[0].points)
        for slave_line in slave_lines:
            #"inject" the points at the beginning of the master line
            master_line.points[0:0] = slave_line.points
            #draw back to the center
            #need to use all the points on the line or this isn't going to look good
            master_line.points[slave_line_len:slave_line_len] = reversed(slave_line.points)
    #move back to where this was actually centered at
    master_line = offset_by(master_line, center)
    return master_line