from sympy import re, im
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
        self.full_point_order = [[],[]]

    def parameterize(self, f_z, n_steps):
        total_list=[[],[]]
        for t in n_steps.linspace(0,1,n_steps+1):
            z=(1-t)*self.complex + t*f_z
            total_list[REAL].append(re(z))
            total_list[IMAG].append(im(z))
        self.point_order=total_list
        self.full_point_order[REAL] = add_reverse(self.point_order[REAL])
        self.full_point_order[IMAG] = add_reverse(self.point_order[IMAG])

    def data_dump(self):
        return {"reals":point_order[REAL],"imaginaries":point_order[IMAG]}

def add_reverse(target):
    """Take a list, reverse it, and extend the original list with that"""
    og_target = list(target) #copy the list to avoid the next line affecting og_target
    target.reverse()
    return og_target + target