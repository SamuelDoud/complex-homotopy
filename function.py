from sympy import I, re, im, Abs, arg, conjugate, Symbol, symbols, lambdify
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import z
import numpy

class function(object):
    def __init__(self, expre):
        self.z=symbols('z',complex=True)
        if isinstance(expre,str):
            self.expre = parse_expr(expre)
        else:
            self.expre=expre
        self.f_z=lambdify(self.z, self.expre, "numpy") #taking advantage of the reuse of the function object. Lamdba numby operations greatly speed up operations on large amounts of data with inital overhead
        
    def evaluateAt(self,w):
        return self.f_z(w) #return the result!

z=symbols('z',complex=True)
funct=function(z**2)
print(funct.evaluateAt(complex(1+1j)))

funct=function("z**2")
print(funct.evaluateAt(complex(1+1j)))

#2j
#z**2