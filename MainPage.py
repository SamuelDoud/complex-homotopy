from tkinter import *
import PointGrid
import plot_window
import function as func
import matplotlib
from builtins import complex
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.master=master
        self.grid = PointGrid.PointGrid()
        self.createWidgets()

    def createWidgets(self):
        self.function_label = Label( root, text="Enter a f(z)")
        self.function_entry = Entry(root, bd=20)
        self.n_label = Label(root, text="Number of steps")
        self.n_entry = Entry(root,bd=5)
        self.interval_label = Label(root, text="Length of interval")
        self.interval_entry = Entry(root,bd=5)
        self.function_label.pack()
        self.function_entry.pack()
        self.n_label.pack()
        self.n_entry.pack()
        self.interval_label.pack()
        self.interval_entry.pack()
        self.submit = Button(root, text ="Submit", command = self.launch)
        self.submit.pack(side =BOTTOM) 
        self.QUIT = Button(self, text="Quit", fg="red", command=root.destroy)
        self.QUIT.pack(side=BOTTOM)

    def launch(self):
        self.grid.circle(1)
        self.grid.grid_lines(complex(-1,1),complex(1,-1),50,50)
        functionObj = func.function(self.function_entry.get())
        self.grid.provide_function(functionObj,int(self.n_entry.get()))
        plot_obj=plot_window.plot_window(self.grid)
        self.update_graph(plot_obj)
        
    def update_graph(self, f):  
        self.canvas = FigureCanvasTkAgg(f.fig,master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        interval=20
        if int(self.interval_entry.get()):
            interval = int(self.interval_entry.get())
        f.animate(interval_length=interval)

root = Tk()
app = Application(master=root)
app.mainloop()
