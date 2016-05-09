from sympy import Function, Symbol, symbols, lambdify, re, im, arg, Abs, E, sympify
from sympy.abc import z

class ComplexFunction(object):
    """
    A class that defines a single function on the complex plane.
    Bugs include that if a string is passed as the epressionn name, then
    the string cannot be evaluatd as an expression. This is accounting for
    the use of Sympify. This leads to being forced to use the eval() built-in
    function. This is much slower than numpy lambdify and is unsafe (as eval
    reads in code, which could be malicious.
    """
    def __init__(self, expression):
        """
        Given a function, in either string or expression format, create an object that
        can evaluate any complex number given to it.
        """
        self.expr = sympify(expression)
        #self.z = symbols('z', complex=True)
        self.f_z = lambdify(z, self.expr, "numpy")
        #taking advantage of the reuse of the function object.
        #Lamdba numby operations greatly speed up operations on
        #large amounts of data with inital overhead

    def evaluate_at_point(self, input):
        """
        Take a z and apply it to the function. Basically returning f(z).
        Additional logic to hand complex number to the correct evalulation
        function.
        """
        try:
            return self.f_z(input)
        except:
            #send the error back to the line class for error handling
            raise ZeroDivisionError
