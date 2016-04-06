import numpy as np
REAL=0
IMAG=1#constants used for point order indexes

class point(object):
    """This class defines a point on a graph and the order in which those points are displayed.
    User must pass a real and imaginary starting position to the point object"""

    def __init__(self, z):
        self.complex=z #save the point's complex number
        self.point_order = [[],[]] #where the point's homotopies will go
        self.full_point_order = [[],[]] #full order is a list that is 2 point orders attached by their tails. Think of the cartoon character CatDog, but just DogDog or CatCat

    def parameterize(self, f_z, n_steps):
        """given the value of this point applied to a function, parameterize its path to that point on the complex plane"""
        total_list=[[],[]]
        for t in np.linspace(0,1,n_steps+1):#range t from 0 to 1 inclusive with n_step + 1 number of evenly spaced steps
            z=(1-t)*self.complex + t*f_z #Dr. Casey's method of parameterizing the homotopy. This is kinda the meat of the entire program
            total_list[REAL].append(z.real) #append the point calculated to the points order
            total_list[IMAG].append(z.imag)
        self.point_order=total_list #point order is the non-reversed list
        self.full_point_order[REAL] = add_reverse(self.point_order[REAL]) #this allows the animation to run in reverse
        self.full_point_order[IMAG] = add_reverse(self.point_order[IMAG])

    def data_dump(self):
        return {"reals":point_order[REAL],"imaginaries":point_order[IMAG]} #only dump the non-reversed list as storing that is pretty redunadant

def add_reverse(target):
    """Take a list, reverse it, and extend the original list with that"""
    #Is there a C/C++ type way to do this with pointers instead of actually copying and using unneeded memory?
    #copy the list to avoid the next line affecting target
    reversed = list(target)
    reversed.reverse()
    return target + reversed