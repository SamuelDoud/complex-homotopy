import numpy as np
REAL=0
IMAG=1#constants used for point order indexes

class point(object):
    """This class defines a point on a graph and the order in which those points are displayed.
    User must pass a real and imaginary starting position to the point object"""

    def __init__(self, z):
        self.complex=z #save the point's complex number
        self.point_order = [] #where the point's homotopies will go
        self.n_steps=1

    def parameterize(self, f_z, n_steps):
        """given the value of this point applied to a function, parameterize its path to that point on the complex plane"""
        total_list=[]
        for z in np.linspace(self.complex,f_z,n_steps+1):#range t from self.complex to f_z inclusive with n_step number of evenly spaced steps
            self.point_order.append((z.real,z.imag))#append a tuple describing the point at this particular spot            
        self.n_steps = len(self.point_order)

    def get_location_at_step(self,step):
        """The user can call for a step and get it back. The reason that a function is used is that the step n_steps + n actually refers to n_steps - n"""
        index = step
        if index >= (self.n_steps):
            index = self.n_steps-(index % self.n_steps)-1 #reversal step
            #could inject code here if reversals aren't wanted
        return self.point_order[index]

def add_reverse(target):
    """Take a list, reverse it, and extend the original list with that"""
    #Is there a C/C++ type way to do this with pointers instead of actually copying and using unneeded memory?
    #copy the list to avoid the next line affecting target
    reversed = list(target)
    reversed.reverse()
    return target + reversed