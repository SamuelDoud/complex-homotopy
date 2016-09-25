import matplotlib.pyplot as plt
from sympy import latex, Symbol, sympify
from sympy.abc import z

class FunctionDisplay:
    """A matplotlib graph that utilizes matplotlib's ability to display LaTeX."""
    def __init__(self, **kwargs):
        self.row_size = 2
        self.column_size = 4
        self.fig = plt.figure(figsize=(self.column_size,self.row_size), dpi=50)
        #plt.show()
        self.latex_str = ""

    def new_input(self, input):
        """Updates the latex display with the new string 'input'."""
        #checks if the input is even worth trying to convert to an expression
        #cheaper than having sympify fail
        if not input[-1].isalnum() and not input[-1] in (')', '}', ']'):
            return
        expr = sympify(input)
        self.latex_str = latex(expr)
        #wipes any previous texts
        self.fig.texts = []
        self.fig.text(0.1,0.5,r"$" + self.latex_str + "$", fontsize=40)
