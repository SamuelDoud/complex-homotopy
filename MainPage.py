from tkinter import Frame, Tk, Checkbutton, Button, Label, Entry, IntVar, BOTTOM, BOTH
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.id_number_counter = 0
        self.line_collection = []
        self.canvas = None
        self.identity = "z"
        self.identity_function = func.ComplexFunction(self.identity)
        #self.pack()
        self.master = master
        self.point_grid = PointGrid.PointGrid()
        self.outlier_remover = IntVar()
        self.outlier_remover.set(0)
        self.create_widgets()
        self.pack_widgets()
        self.animating_already = False
        self.build_sample()
        #show the graph
        self.launch()

    def create_widgets(self):
        """
        Creates and arranges the GUI.
        """
        common_bd = 5
        #checkbox to control outlier logic
        self.outlier_remover_check_box = Checkbutton(self, text="Remove outliers",
                                                     variable=self.outlier_remover,
                                                     onvalue=1, offvalue=0, height=5, width=20)
        self.submit = Button(ROOT, text="Submit", command=self.launch)
        self.function_label = Label(ROOT, text="Enter a f(z)")
        self.save_video = Button(ROOT, text="Save as Video", command=self.save_video_handler)
        self.interval_label = Label(ROOT, text="Length of interval")
        self.n_label = Label(ROOT, text="Number of steps")
        self.real_max_label = Label(ROOT, text="Real max")
        self.real_min_label = Label(ROOT, text="Real min")
        self.imag_max_label = Label(ROOT, text="Imag max")
        self.imag_min_label = Label(ROOT, text="Imag min")
        self.real_max_entry = Entry(ROOT, bd=common_bd)
        self.real_min_entry = Entry(ROOT, bd=common_bd)
        self.imag_min_entry = Entry(ROOT, bd=common_bd)
        self.imag_max_entry = Entry(ROOT, bd=common_bd)
        self.function_entry = Entry(ROOT, bd=common_bd)
        self.n_entry = Entry(ROOT, bd=common_bd)
        self.interval_entry = Entry(ROOT, bd=common_bd)

    def pack_widgets(self):
        """
        Method to pack widgets created in above method onto the window.
        This method only exists for organization purposes.
        Pythonically, this code is probably bad. I am referencing variables that are created
        outside of this method but not in the __init__ method.
        """
        self.submit.grid(row=5, column=1, columnspan=2)
        self.outlier_remover_check_box.grid(row=5, column=0)
        self.save_video.grid(row=6, column=0, columnspan=3)
        self.function_label.grid(row=2, column=0)
        self.function_entry.grid(row=2, column=1)
        self.n_label.grid(row=3, column=0)
        self.n_entry.grid(row=3, column=1)
        self.interval_label.grid(row=4, column=0)
        self.interval_entry.grid(row=4, column=1)
        self.real_max_label.grid(row=2, column=3)
        self.real_max_entry.grid(row=2, column=4)
        self.real_min_label.grid(row=2, column=6)
        self.real_min_entry.grid(row=2, column=5)
        self.imag_min_label.grid(row=3, column=6)
        self.imag_min_entry.grid(row=3, column=5)
        self.imag_max_label.grid(row=3, column=3)
        self.imag_max_entry.grid(row=3, column=4)

    def add_to_collection(self, lines):
        """
        Adds a set of lines to the collection and appends a id tag
        """
        self.line_collection.append((lines, self.id_number_counter))
        #increment the id tag
        self.id_number_counter += 1
        #return the id tag less one (as to refer to this object)
        return self.id_number_counter - 1

    def remove_from_collection(self, id_number=None):
        """
        Removes a line collection from the list.
        """
        #search for the line
        #This is an ordered set. Using a binary search
        #did the user pass a value for id_number?
        if id_number:
            try:
                length = len(self.line_collection)
                index = length // 2
                last_index = index + 1
                #how much to move the index by every step
                delta = index // 2 + 1
                while self.line_collection[index][1] != id_number:
                    if self.line_collection[index][1] > id_number:
                        index -= delta
                    else:
                        index += delta
                    if last_index == index:
                        return False
                    last_index = index
                    delta //= 2
                self.line_collection.pop(index)
                self.point_grid.new_lines(self.flattend_lines())
                return True
            except IndexError:
                return False
        else:
            if self.line_collection:
                #successfully popped a set of lines from the stack
                self.line_collection.pop()
                return True
            else:
                return False

    def build_sample(self):
        """
        A sampler method to test adding and removing shapes.
        """
        id1 = self.add_lines(self.point_grid.circle(1))
        id2 = self.add_lines(self.point_grid.grid_lines(complex(-1, 1), complex(1, -1), 10, 10))
        self.remove_from_collection(id1)

    def flattend_lines(self):
        """
        The collection of lines is a list of tuples with
        each tuple containing a list of lines and an id.
        This method takes all the lines in the collection
        and returns them as one list.
        """
        stripped_of_id = [line[0] for line in self.line_collection]
        return [item for sublist in stripped_of_id for item in sublist]

    def add_lines(self, list_of_lines):
        """
        Given a list of lines, add them to the Plot.
        """
        if not isinstance(list_of_lines, list):
            list_of_lines = [list_of_lines]
        for line in list_of_lines:
            self.point_grid.add_line(line)
        return self.add_to_collection(list_of_lines)

    def build_circle(self, radius, center=complex(0, 0)):
        """
        Build a circle from a popup
        """
        return self.add_lines(self.point_grid.circle(radius, center))

    def build_grid(self, upper_right, lower_left, lines_num):
        """
        Build a grid from a popup.
        """
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
        self.point_grid.set_user_limits(self.fetch_limits())
        if self.function_entry.get():
            self.current_function = self.function_entry.get()
            try:
                #check if the fuction is valid
                function_object = func.ComplexFunction(self.current_function)
            except Exception:
                #fallback to the identity
                function_object = self.identity_function
        else:
            function_object = self.identity_function
        try:
            steps_from_user = int(self.n_entry.get())
        except Exception:
            steps_from_user = 1 #no animation
        #interval cannot be changed after launch
        self.point_grid.provide_function(function_object, steps_from_user, self.flattend_lines())
        if not self.animating_already:
            self.plot_object = PlotWindow.PlotWindow(self.point_grid)
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

    def fetch_limits(self):
        """
        Get the limits the user put into the GUI.
        Apply logical checking (maxes must be greater than mins...
        Also insert Nones for blanks or invalid entries
        Limits arranged in a tuple as follows:
        (Real max, real min, imaginary max, imaginary min)
        """
        real_max = self.get_limit_from_entry(self.real_max_entry)
        real_min = self.get_limit_from_entry(self.real_min_entry)
        imag_max = self.get_limit_from_entry(self.imag_max_entry)
        imag_min = self.get_limit_from_entry(self.imag_min_entry)
        all_clear = True
        limits = (real_max, real_min, imag_max, imag_min)
        if None in limits:
            all_clear =  False
        else:
            if real_max <= real_min or imag_max <= imag_min:
                all_clear = False
        if all_clear:
            return limits
        else:
            return (None, None, None, None)

    def get_limit_from_entry(self, limit_entry):
        """
        Given a limit entry, determine its value if it is a number.
        """
        #this variable acts as the sign of the user data
        multiplier = 1
        limit_entry_string = str(limit_entry.get())
        #replace the FIRST negative sign seen
        is_there_a_negative_sign = limit_entry_string.replace("-", "", 1)
        if is_there_a_negative_sign is not limit_entry_string:
            #the user gave a negative sign, but we had to remove it
            multiplier = -1
        #check if the use passed something legal
        if not is_there_a_negative_sign.isnumeric():
            return None
        else:
            #return the numeric value of the user data multiplied by its sign
            return float(is_there_a_negative_sign)*multiplier


    def update_graph(self, plot_object):
        """
        Create the frame on which the matplotlib figure will be displayed.
        Also, kick off the animation.
        """
        self.canvas = FigureCanvasTkAgg(plot_object.fig, master=ROOT)
        #self.canvas.show()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=6)
        #self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        try:
            interval = int(self.interval_entry.get())
        except ValueError:
            interval = 20
        self.animating_already = True
        plot_object.animate(interval_length=interval)

    def circle_builder_popup(self):
        pass

    def grid_builder_popup(self):
        pass

ROOT = Tk()
WINDOW = Application(master=ROOT)
WINDOW.mainloop()
