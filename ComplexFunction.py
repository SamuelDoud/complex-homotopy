from sympy import Function, Symbol, symbols, lambdify, re, im, arg, Abs

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
        self.use_eval = False #work to get rid of this
        if isinstance(expression, str):
            self.use_eval = True
            self.expr = expression
        else:
            self.expr = expression
            self.z = symbols('z', complex=True)
            self.f_z = lambdify(self.z, self.expr, "numpy")
        #taking advantage of the reuse of the function object.
        #Lamdba numby operations greatly speed up operations on
        #large amounts of data with inital overhead

    def evaluate_at_point(self, z):
        """
        Take a z and apply it to the function. Basically returning f(z).
        Additional logic to hand complex number to the correct evalulation
        function.
        """
        try:
            #the two cases of evaluation. The dirty eval or the clean lambdify.
            if self.use_eval:
                return eval(self.expr)
            return self.f_z(z)
        except:
            #send the error back to the line class for error handling
            raise ZeroDivisionError
