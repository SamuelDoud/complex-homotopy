import sys

from sympy import (Function, Symbol, symbols, lambdify, re, im, arg, Abs, E, sympify, sin, sinc,
                   cos, cosh, acos, acosh, acot, acoth, acsc, asec, asech, asin, asinh,
                   atan, atan2, atanh, conjugate, tan, tanh, pi, log, ln)
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
    #indentity functionn for external classes to use

    def __init__(self, expression):
        """
        Given a function, in either string or expression format, create an object that
        can evaluate any complex number given to it.
        """
        self.function_str = compliant_expression(expression)
        self.filename = generate_filename(expression)
        try:
            #TODO regex cleaning of expression
            self.expr = sympify(self.function_str)
            #self.z = symbols('z', complex=True)
            self.f_z = lambdify(z, self.expr, "numpy")
        except:
            print("Illegal expression: ", sys.exc_info()[0])
        #taking advantage of the reuse of the function object.
        #Lamdba numby operations greatly speed up operations on
        #large amounts of data with inital overhead

    def evaluate_at_point(self, point_in_domain):
        """
        Take a z and apply it to the function. Basically returning f(z).
        Additional logic to hand complex number to the correct evalulation
        function.
        """
        try:
            return self.f_z(point_in_domain)
        except:
            #send the error back to the line class for error handling
            raise ZeroDivisionError

def compliant_expression(expression):
    """
    Take the passed expression and change it so that it can be understood by sympify.
    """
    #this may not be a string
    expression = str(expression)
    expression = expression.upper()
    expression = expression.replace("PI", "pi")
    expression = expression.replace("EXP", "E**")
    expression = expression.lower()
    expression = expression.replace("e", "E")
    return expression

def generate_filename(expression):
    """
    Takes the expression and generates a filename from it
    removes the illegal characters and such
    """
    #only do if the expression is a string (passed by user)
    if isinstance(expression, str):
        expression = expression.replace("**", "_to_the_")
        expression = expression.replace("+", "_plus_")
        expression = expression.replace("-", "_minus_")
        expression = expression.replace("/", "_divided_by_")
        expression = expression.replace("*", "_times_")
        return expression
    return None


