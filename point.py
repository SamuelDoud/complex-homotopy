import cmath
import pickle

REAL=0
IMAG=1#constants used for point order indexes

class point(object):
    """This class defines a point on a graph and the order in which those points are displayed.
    User must pass a real and imaginary starting position to the point object"""

    def __init__(self, z):
        self.real = z.real
        self.imag = z.imag
        self.complex=z
        self.point_order = [[],[]]

    def parameterize(self, f_z, n_steps):
        total_list=[[],[]]
        for t in [step/n_steps for step in range(n_steps+1)]:
            z=(1-t)*self.complex + t*f_z
            total_list[REAL].append(z.real)
            total_list[IMAG].append(z.imag)
        self.point_order=total_list

    def data_dump(self):
        return {"reals":point_order[REAL],"imaginaries":point_order[IMAG]}