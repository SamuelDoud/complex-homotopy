import numpy as np

#constants used for point order indexes
REAL = 0
IMAG = 1

class ComplexPoint(object):
    """
    This class defines a point on a graph and the order in which those points are displayed.
    User must pass a complex starting position to the point object
    """

    def __init__(self, z, ignore_in_outliers=False):
        self.complex = z #save the point's complex number
        self.point_order = [] #where the point's homotopies will go
        self.n_steps = 1
        self.ignore_in_outliers = ignore_in_outliers

    def parameterize(self, f_z, n_steps, append=False):
        """
        Given the value of this point applied to a function, parameterize its path
        to that point on the complex plane
        """
        #append a tuple describing the point at this particular spot
        if not append:
            self.point_order = [((z.real, z.imag)) for z in np.linspace(self.complex, f_z,
                                                                        n_steps)]
        else:
            last = self.point_order[-1]
            self.point_order = (self.point_order[:-1] +
                                [((z.real, z.imag)) for z in np.linspace(complex(last[REAL],
                                                                                 last[IMAG]),
                                                                         f_z, n_steps)])
        self.n_steps = len(self.point_order)

    def get_location_at_step(self, step):
        """
        The user can call for a step and get it back.
        The reason that a function is used is that the step n_steps + n
        actually refers to n_steps - n
        """
        index = step
        if index >= (self.n_steps):
            #reversal step logic
            index = self.n_steps-(index % self.n_steps) - 1
            #could inject code here if reversals aren't wanted
        try:
            return self.point_order[index]
        except IndexError:
            return None

    def add_reverse_to_point_order(self):
        """
        Take the point order and merge its head to its tail to emulate a loop
        """
        if len(self.point_order) > 1:
            self.point_order = self.point_order[:-1] + list(reversed(self.point_order))
            self.n_steps = len(self.point_order)
