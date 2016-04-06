import numpy
from sympy import Function, Symbol, symbols, lambdify,re, im, arg, Abs

class function(object):
    def __init__(self, expression):
            self.expr=expression
            self.z=symbols('z',complex=True)
            self.f_z=lambdify(self.z, self.expr, "numpy") #taking advantage of the reuse of the function object. Lamdba numby operations greatly speed up operations on large amounts of data with inital overhead
    def evaluateAt(self,z):
        return self.f_z(z)

