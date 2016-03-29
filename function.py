from sympy import I, re, imageop, Abs, arg, conjugate, expand, rewrite
import cmath
z = symbols('z', complex=True) #establish z as a complex number
class function(object):
    """description of class"""
    def __init__(self, expression):
        """Take an expression and parse it"""
        expression = str(expression)
        expression.replace("i", "I") #sympy prefers uppercase I to denote the imaginary unit
        self.expression = expression.expand(complex=True)
        self.real_part = re(expression)
        self.imag_part = im(expression)
    def evaluateAt(z):
        real_z = z.real
        imag_z = z.imag #break up z in to its real and imaginary parts
        real_f_z = self.real_part.subs({z:real_z}).n()
        imag_f_z = self.imag_part.subs({z:imag_z}).n()#take the real and imaginary parts of the expression and evaluate them with respect to re(z) and im(z)
        return complex(real_f_z, imag_f_z) #return the result!