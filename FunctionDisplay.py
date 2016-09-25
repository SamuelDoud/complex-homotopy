import matplotlib.pyplot as plt
from sympy import latex, Symbol, sympify
from sympy.abc import z

class FunctionDisplay:
    """A matplotlib graph that utilizes matplotlib's ability to display LaTeX."""
    def __init__(self, **kwargs):
        self.row_size = 3
        self.column_size = 6
        self.fig = plt.figure(figsize=(self.column_size, self.row_size), dpi=50, facecolor="#F0F0F0")
        self.identity = latex(sympify("z"))
        self.latex_str = ""

    def new_input(self, input):
        """Updates the latex display with the new string 'input'."""
        #checks if the input is even worth trying to convert to an expression
        #cheaper than having sympify fail
        if not input[-1].isalnum() and not input[-1] in (')', '}', ']'):
            return
        if input == "z":
            self.latex_str = self.identity
        else:
            expr = sympify(input)
            self.latex_str = latex(expr)
        #wipes any previous texts
        self.fig.texts = []
        self.fig.text(0.1, 0.5, r"$" + self.latex_str + "$", fontsize=40)
        self.fig.tight_layout()