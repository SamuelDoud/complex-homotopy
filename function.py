from sympy import I, re, im, Abs, arg, conjugate, expand, Symbol, symbols, lambdify
from sympy.abc import z
import cmath
import numpy
class function(object):
    """description of class"""
    def __init__(self, expression):
        """Take an expression and parse it"""
        self.z=symbols('z',complex=True)
        self.expression=expression
        self.f_z=lambdify(self.z, self.expression, "numpy") #taking advantage of the reuse of the function object. Lamdba numby operations greatly speed up operations on large amounts of data with inital overhead
        
    def evaluateAt(self,w):
        return complex(self.f_z(w)) #return the result!
    