from tkinter import Frame, Tk, Checkbutton, Button, Label, Entry, IntVar, BOTTOM, BOTH
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import PointGrid
import PlotWindow
import ComplexFunction as func

class Application(Frame):
    """
    This is the window that displays the homotopy. Also it provides an interface for the user to
    manipulate the homotopy as they see fit.
    """
    def __init__(self, master=None):
        """
        A generic init function. Creates some class variables for later use.
        Calls on the function to create widgets and eventually, launches the window.
        """
        Frame.__init__(self, master)
        self.id = 0
        self.line_collection = []
        
        self.canvas = None
        self.identity = "z"
        self.identity_function = func.ComplexFunction(self.identity)
        self.pack()
        self.master = master
        self.grid = PointGrid.PointGrid()
        self.outlier_remover = IntVar()
        self.outlier_remover.set(0)
        self.create_widgets()
        self.animating_already = False
        self.build_sample()
        #show the graph
        self.launch()

    def create_widgets(self):
        """
        Creates and arranges the GUI.
        """
        self.outlier_remover_check_box = Checkbutton(self, text="Remove outliers",
                                                     variable=self.outlier_remover,
                                                     onvalue=1, offvalue=0, height=5, width=20)
        self.save_video = Button(self, text="Save as Video", command=self.save_video_handler)
        self.function_label = Label(root_of_tkinter, text="Enter a f(z)")
        self.function_entry = Entry(root_of_tkinter, bd=20)
        self.n_label = Label(root_of_tkinter, text="Number of steps")
        self.n_entry = Entry(root_of_tkinter, bd=5)
        self.interval_label = Label(root_of_tkinter, text="Length of interval")
        self.interval_entry = Entry(root_of_tkinter, bd=5)
        self.submit = Button(self, text="Submit", command=self.launch)
        self.submit.pack(side=BOTTOM)
        self.quit = Button(self, text="Quit", fg="red", command=root_of_tkinter.destroy)
        self.quit.pack(side=BOTTOM)
        self.outlier_remover_check_box.pack(side=BOTTOM)
        self.save_video.pack(side=BOTTOM)
        self.function_label.pack()
        self.function_entry.pack()
        self.n_label.pack()
        self.n_entry.pack()
        self.interval_label.pack()
        self.interval_entry.pack()

    def add_to_collection(self, lines):
        """
        Adds a set of lines to the collection and appends a id tag
        """
        self.line_collection.append((lines, self.id))
        #increment the id tag
        self.id += 1
        #return the id tag less one (as to refer to this object)
        return self.id - 1
    
    def remove_from_collection(self, id):
        """
        Removes a line collection from the list.
        """
        #search for the line
        #TODO, this is an ordered set. Use a binary search
        length = len(self.line_collection)
        index = length // 2
        last_index = index + 1
        delta = index // 2
        while self.line_collection[index][1] != id:
            if self.line_collection[index][1] > id:
                index -= delta
            else:
                index += delta
            if last_index == index:
                return False
            last_index = index
            delta //= 2
        self.line_collection.pop(index)
        self.grid.new_lines(self.flattend_lines())
        return True

    def build_sample(self):
        id1 = self.add_lines(self.grid.circle(1))
        id2 = self.add_lines(self.grid.grid_lines(complex(-1, 1), complex(1, -1), 10, 10))
        self.remove_from_collection(id2)
    
    def flattend_lines(self):
        stripped_of_id = [line[0] for line in self.line_collection]
        return [item for sublist in stripped_of_id for item in sublist]
        
    def add_lines(self, list_of_lines):
        """
        Given a list of lines, add them to the Plot.
        """
        if not isinstance(list_of_lines, list):
            list_of_lines = [list_of_lines]
        for line in list_of_lines:
            self.grid.add_line(line)
        return self.add_to_collection(list_of_lines)

    def build_circle(self, radius, center=complex(0,0)):
        return self.add_lines(self.grid.circle(radius,center))

    def build_grid(self, upper_right, lower_left, lines_num):
        return self.add_lines(self.grid.grid_lines(upper_right, lower_left, lines_num, lines_num))
    def save_video_handler(self):
        """
        Dispatches the Plot to save the video.
        Should implement a filename prompt.
        """
        self.plot_object.save(self.current_function, video=True)

    def launch(self):
        """
        Create a new animation based on the data given by the user.
        This method will be called on the press of the submit button.
        """
        #take the input from the user.. if its null, set ito the identity function
        if self.function_entry.get():
            self.current_function = self.function_entry.get()
            try:
                #check if the fuction is valid
                function_object = func.ComplexFunction(self.current_function)
            except:
                #fallback to the identity
                function_object = self.identity_function
        else:
            function_object = self.identity_function
        try:
            steps_from_user = int(self.n_entry.get())
        except:
            steps_from_user = 1 #no animation
        #interval cannot be changed after launch
        self.grid.provide_function(function_object, steps_from_user, self.flattend_lines())
        if not self.animating_already:
            self.plot_object = PlotWindow.PlotWindow(self.grid)
            self.update_graph(self.plot_object)
        else:
            try:
                interval = int(self.interval_entry.get())
            except ValueError:
                interval = 20
            self.plot_object.anim._interval = interval
        #set the boolean that controls the outlier operation in the pointgrid to that of the user
        self.plot_object.grid.remove_outliers = self.outlier_remover.get() == 1
        self.plot_object.new_limits()

    def update_graph(self, plot_object):
        """
        Create the frame on which the matplotlib figure will be displayed.
        Also, kick off the animation.
        """
        self.canvas = FigureCanvasTkAgg(plot_object.fig, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        try:
            interval = int(self.interval_entry.get())
        except ValueError:
            interval = 20
        self.animating_already = True
        plot_object.animate(interval_length=interval)


root_of_tkinter = Tk()
WINDOW = Application(master=root_of_tkinter)
WINDOW.mainloop()
