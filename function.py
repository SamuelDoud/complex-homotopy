import numpy
from sympy import Function, Symbol, symbols, lambdify
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, split_symbols_custom, _token_splittable

class function(object):
    def __init__(self, expression):
        if isinstance(expression, str):
            self.z=symbols('z',complex=True)
            transformations=standard_transformations + (implicit_multiplication,)
            self.evaluator=function(parse_expr(expression, transformations=transformations))
            self.flag=True
        else:
            self.z=symbols('z',complex=True)
            self.f_z=lambdify(self.z, expression, "numpy") #taking advantage of the reuse of the function object. Lamdba numby operations greatly speed up operations on large amounts of data with inital overhead
            self.flag=False
    def evaluateAt(self,z):
        if self.flag:
            return self.evaluator.evaluateAt(z)
        return self.f_z(z)

class nested_function(Function):

    @classmethod
    def eval(cls, expr, sym):
        # automatic evaluation should be done here
        # return None if not required
        return None


    def evaluateAt(self, pt):
        return self.args[0].subs(self.args[1], pt)

s = function("z**2")
print(s.evaluateAt(complex(1 + 1j)).expand())