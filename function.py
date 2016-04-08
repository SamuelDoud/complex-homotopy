import numpy
from sympy import Function, Symbol, symbols, lambdify,re, im, arg, Abs

class function(object):
    def __init__(self, expression):
            self.use_eval=False #work to get rid of this
            if isinstance(expression, str):
                self.use_eval = True
                self.expr = expression
            else:
                self.expr=expression
                self.z=symbols('z',complex=True)
                self.f_z=lambdify(self.z, self.expr, "numpy") #taking advantage of the reuse of the function object. Lamdba numby operations greatly speed up operations on large amounts of data with inital overhead

    def evaluateAt(self,z):
        if self.use_eval:
            return eval(self.expr)
        return self.f_z(z)

