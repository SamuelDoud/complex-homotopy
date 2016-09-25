import pickle
import threading
import os
import sys
from itertools import cycle
import math

from tkinter import (Frame, Tk, Checkbutton, Button, Label, Entry, IntVar, messagebox, StringVar,
                     Scale, END, HORIZONTAL, Menu, filedialog, colorchooser, RIGHT, LEFT)
import tkinter
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler
from sympy import latex, Symbol, sympify
from sympy.abc import z

import PointGrid
import PlotWindow
import ComplexFunction as func
import ComplexPoint
import Line
import PreferencesWindow
import BuilderWindows
import ShapesMenu
import ZoomWindow
import NavigationBar
import GridLinesWindow
import FunctionDisplay

matplotlib.use("TkAgg")

#constants for checkboxes
ON = 1
OFF = 0

DATA = 0
ID = 1

PAUSE_FLAG = True
PLAY_FLAG = False

PLAYING = "Playing"
PAUSED = "Paused"
COMPUTING = "Computing"

def allow_constants(string_to_strip_of_constants):
    string_to_strip_of_constants = str(string_to_strip_of_constants).upper()
    pi_const_str = str(math.pi)
    e_const_str = str(math.e)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("PI", pi_const_str)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("E", e_const_str)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("I", "j")
    string_to_strip_of_constants = string_to_strip_of_constants.replace("J", "j")
    string_to_strip_of_constants = string_to_strip_of_constants.replace("*", "")
    return string_to_strip_of_constants

def convert_to_byte_color(tuple_colors_zero_to_one):
    list_colors_zero_to_one = list(tuple_colors_zero_to_one)
    for index, color in enumerate(list_colors_zero_to_one):
        list_colors_zero_to_one[index] = int(color * 255)
    return tuple(list_colors_zero_to_one)

def convert_to_zero_to_one(tuple_three_byte_color):
    list_three_byte_color = list(tuple_three_byte_color)
    for index, color in enumerate(list_three_byte_color):
        list_three_byte_color[index] = color / 256
    return tuple(list_three_byte_color)

class Application(Frame):
    """
    This is the window that displays the homotopy. Also it provides an interface for the user to
    manipulate the homotopy as they see fit.
    """
    def __init__(self, master):
        """
        A generic init function. Creates some class variables for later use.
        Calls on the function to create widgets and eventually, launches the window.
        """
        Frame.__init__(self, master)
        self.master = master
        self.master.title("Complex Homotopy")
        self.master.protocol("WM_DELETE_WINDOW", self.shutdown)
        #give the icon file to the GUI
        #uncoment this when I figure out pyInstaller
        self.image_loading()
        self.master.iconphoto(True, self.application_icon)
        #how long between frames in milliseconds
        self.default_interval = 40
        self.default_points_on_line = 150
        self.attributes = {}
        self.z = Symbol('z')
        self.function_display = FunctionDisplay.FunctionDisplay()
        self.function_str = StringVar()
        self.function_str.set("")
        self.function_str.trace("w", self.update_latex)
        self.fps_str = "Frames per second"
        self.n_points_str = "Default points per line"
        self.attributes[self.fps_str] = 1000 / self.default_interval
        self.attributes[self.n_points_str] = self.default_points_on_line
        self.animation_thread = None
        self.start_color = (0, 0, 0)
        self.end_color = (0, 0, 0)
        self.extensions = [("Homotopy data", ".cht"), ("All Files", "*")]
        self.default_extension = ".cht"
        self.lines_pickle_str = "lines"
        self.limits_pickle_str = "limits"
        self.id_counter_pickle_str = "id_counter"
        self.n_steps_pickle_str = "n_steps"
        self.functions_pickle_str = "functions"
        self.reverse_checkbox_pickle_str = "reverse"
        self.outlier_remover_pickle_str = "outlier"
        self.type_strs = {}
        self.type_strs["disk"] = "disk"
        self.type_strs["circle"] = "circle"
        self.type_strs["grid"] = "grid"
        self.type_strs["ellipse"] = "ellipse"
        self.type_strs["line"] = "line"
        self.type_strs["spindle"] = "spindle"
        self.function_objects = []
        self.id_number_counter = 0
        self.line_collection = []
        self.canvas = None
        self.toolbar = None
        self.frame_slider = None
        self.plot_object = None
        self.n_steps_per_function = 0
        self.size = 7
        self.slider_row = 2
        self.slider_column = 0
        self.identity = "z"
        self.identity_function = func.ComplexFunction(self.identity)
        self.point_grid = PointGrid.PointGrid()
        self.outlier_remover_var = IntVar()
        self.outlier_remover_var.set(OFF)
        self.reverse_checkbox_var = IntVar()
        self.reverse_checkbox_var.set(OFF)
        self.view_grids_checkbox_var = IntVar()
        self.view_grids_checkbox_var.set(ON)
        self.reverse = False
        self.remove_outliers = False
        self.create_frames()
        self.create_widgets()
        self.grid_widgets_in_frames()
        self.grid_frames()
        self.animating_already = False
        self.animating_already_secondary = False
        self.already_paused = False
        self.lock_frame = False
        self.popup_window = None
        self.build_sample()
        self.menu_creation()
        self.function_entry.focus()
        #show the graph
        self.launch()

    def image_loading(self):
        """Load the file path to images necessary for the function of this program
        Loading spinner: https://commons.wikimedia.org/wiki/File:Loading_icon.gif"""
        images = "images"
        #scale_w = new_width/old_width
        #scale_h = new_height/old_height
        if os.name == "nt":
            #account for the difference between Windows and Unix file systems
            images = images + "\\"
        else:
            images = images + "/"
        self.play_icon_path = resource_path(images + "play.png")
        self.pause_icon_path = resource_path(images + "pause.png")
        self.loading_spinner_icon_path = resource_path(images + "Loading_icon_cropped.gif")
        self.application_icon_path = resource_path(images + "icon.png")
        self.zoom_in_icon_path = resource_path(images + "zoom_in.png")
        self.zoom_out_icon_path = resource_path(images + "zoom_out.png")
        self.frame_increment_icon_path = resource_path(images + "frame_increment.png")
        self.frame_decrement_icon_path = resource_path(images + "frame_decrement.png")
        self.go_to_range_icon_path = resource_path(images + "range.png")
        self.go_to_domain_icon_path = resource_path(images + "domain.png")
        self.save_gif_icon_path = resource_path(images + "GIF_icon.png")
        self.save_movie_icon_path = resource_path(images + "movie_icon.png")
        
        self.play_icon = tkinter.PhotoImage(file=self.play_icon_path)
        self.pause_icon = tkinter.PhotoImage(file=self.pause_icon_path)
        self.loading_spinner_icon = tkinter.PhotoImage(file=self.loading_spinner_icon_path)
        self.application_icon = tkinter.PhotoImage(file=self.application_icon_path)
        self.zoom_in_icon = tkinter.PhotoImage(file=self.zoom_in_icon_path)
        self.zoom_out_icon = tkinter.PhotoImage(file=self.zoom_out_icon_path)
        self.frame_decrement_icon = tkinter.PhotoImage(file=self.frame_decrement_icon_path)
        self.frame_increment_icon = tkinter.PhotoImage(file=self.frame_increment_icon_path)
        self.go_to_domain_icon = tkinter.PhotoImage(file=self.go_to_domain_icon_path)
        self.go_to_range_icon = tkinter.PhotoImage(file=self.go_to_range_icon_path)
        self.save_gif_icon = tkinter.PhotoImage(file=self.save_gif_icon_path)
        self.save_movie_icon = tkinter.PhotoImage(file=self.save_movie_icon_path)


    def shutdown(self):
        """
        Closes the application
        """
        self.master.quit()
        self.master.destroy()

    def key_bindings(self):
        """
        Bind the keys.
        """
        self.master.bind("<Return>", self.launch)
        self.master.bind("<Right>", self.increment_frame)
        self.master.bind("<Left>", self.decrement_frame)
        self.master.bind("<Up>", self.interval_decrease)
        self.master.bind("<Down>", self.interval_increase)
        self.master.bind_all("<MouseWheel>", self.zoom_mousewheel)
        #self.master.bind("<space>", self.plot_object.toggle_pause)
        #space is a bad idea for pausing in a application that offers typing
        #self.master.bind("<p>", self.plot_object.toggle_pause)

    def zoom_mousewheel(self, event):
        """Zoom in/out by event."""
        self.plot_object.zoom_on_delta(event.delta/1200)

    def zoom_out_step(self, proportion=-.1):
        """Zoom out by proportion."""
        self.plot_object.zoom_on_delta(proportion)

    def zoom_in_step(self, proportion=.1):
        """Zoom in by proportion."""
        self.plot_object.zoom_on_delta(proportion)

    def increment_frame(self, event=None):
        """
        go forward one frame
        """
        self.move_frame(1)

    def decrement_frame(self, event=None):
        """
        Move back one frame
        """
        self.move_frame(-1)

    def move_frame(self, delta_frames):
        """
        move the animation by delta frames
        """
        if not self.lock_frame:
            self.lock_frame = True
            was_paused_flag = True
            if not self.plot_object.pause:
                self.pause_play(was_paused_flag)
                was_paused_flag = False
            self.plot_object.frame_number += delta_frames
            if was_paused_flag:
                #this will allow one frame to draw
                self.plot_object.pause_override = True
            self.pause_play(was_paused_flag)
            self.lock_frame = False

    def interval_increase(self, event):
        """
        Increase the interval between frames.
        """
        self.plot_object.reset_interval(10)

    def interval_decrease(self, event):
        """
        Decrease the interval between frames
        """
        self.plot_object.reset_interval(-10)

    def menu_creation(self):
        """
        Helper method to define the menu bar
        """
        self.menubar = Menu(self.master)
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.edit_menu = Menu(self.menubar, tearoff=0)
        self.view_menu = Menu(self.menubar, tearoff=0)
        self.help_menu = Menu(self.menubar, tearoff=0)
        self.object_menu = Menu(self.menubar, tearoff=0)
        self.color_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.edit_menu_create()
        self.object_menu_create()
        self.color_menu_create()
        self.file_menu_create()
        self.help_menu_create()
        self.view_menu_create()
        self.master.config(menu=self.menubar)

    def edit_menu_create(self):
        """Method to create the edit menu options."""
        self.edit_menu.add_cascade(label="Objects", menu=self.object_menu)
        self.edit_menu.add_cascade(label="Colors", menu=self.color_menu)
        self.edit_menu.add_command(label="Preferences", command=self.launch_preferences)

    def view_menu_create(self):
        """Method to create the view menu options."""
        self.view_menu.add_cascade(label="Zoom Window", command=self.zoom_window)
        self.view_menu.add_cascade(label="Zoom Square", command=self.force_square)
        self.view_menu.add_cascade(label="Zoom Out", command=self.zoom_out_step)
        self.view_menu.add_cascade(label="Zoom In", command=self.zoom_in_step)
        self.view_menu.add_separator()
        self.view_menu.add_checkbutton(label="Grid Lines", command=self.grid_lines_control,
                                       variable=self.view_grids_checkbox_var, onvalue=ON,
                                       offvalue=OFF)
        self.view_menu.add_cascade(label="Grid Lines Configuration",
                                   command=self.grid_lines_configuration)
        
    def grid_lines_control(self, turn_on=None):
        previous_state = self.pause_play(COMPUTING)
        action = False
        if turn_on == True or self.view_grids_checkbox_var.get() == ON:
            #self.view_grids_checkbox_var.set(IntVar(value=ON))
            action = True
        #else:
        #    #self.view_grids_checkbox_var.set(IntVar(value=OFF))
        self.plot_object.set_grid_lines(visible=action)
        self.pause_play(previous_state)

    def grid_lines_configuration(self, event=None):
        """Prompt the user for information about how the grid lines should be configured"""
        self.general_popup(GridLinesWindow.GridLinesWindow, self.grid_lines_control)

    def zoom_window(self, event=None):
        """Launches the "zoom window" which allows the user to set their own limits"""
        was_paused = self.pause_play(PlotWindow.PAUSE)
        self.popup_window = ZoomWindow.ZoomWindow(self.master)
        self.master.wait_window(self.popup_window.top)
        limits = (self.popup_window.real_max, self.popup_window.real_min,
                  self.popup_window.imag_max, self.popup_window.imag_min)
        for limit in limits:
            limit = allow_constants(limits)
        #ensure that all the limits are numbers and that the limits are properly ordered
        if limits.count(None) == 0 and is_properly_ordered(*limits):
            self.point_grid.set_user_limits(limits)
            self.plot_object.new_limits()
        self.popup_window = None
        self.pause_play(was_paused)

    def force_square(self, event=None):
        self.point_grid.force_square()
        self.plot_object.new_limits()

    def toggle_pause(self, event=None):
        """Toggle the pause state by XOR"""
        return self.pause_play(self.plot_object.pause ^ True)

    def pause_play(self, to_pause=None):
        """Pauses or plays the animation based on to_pause.
        Also will set the label indictating playing or paused.
        Return the status of the animation before the pause call was made"""
        if to_pause == None:
            to_pause = not self.plot_object.pause
        if to_pause == COMPUTING:
            self.pause_play_label.config(text=COMPUTING)
            self.pause_play_button.config(image=self.loading_spinner_icon)
            return self.plot_object.pause
        if to_pause:
            self.pause_play_button.config(image=self.play_icon)
        else:
            self.pause_play_button.config(image=self.pause_icon)
        self.pause_play_label.config(text=PAUSED if to_pause else PLAYING)
        if not self.animating_already_secondary:
            self.animating_already_secondary = True
            self.pause_play_button.config(image=self.play_icon)
            self.pause_play_label.config(text="Awaiting function")
        return self.plot_object.set_animation(to_pause)

    def pause_play_button_flip(self, event=None):
        """Change the play state of the animation and change the image accordingly"""
        self.pause_play()


    def go_to_last_frame(self, event=None):
        """Go to the last frame of the animation and pause on it."""
        self.go_to_frame_int(self.point_grid.n_steps - 1)

    def go_to_first_frame(self,event=None):
        """Go to the first frame of the animation and pause on it."""
        self.go_to_frame_int(0)

    def go_to_frame_int(self, frame_number):
        """Go to the frame_number of the animation and pause on it"""
        self.plot_object.frame_number = frame_number
        self.move_frame(0)
        self.pause_play(PAUSE_FLAG)
        self.master.update()

    def launch_preferences(self):
        #pause the window and see if the user already paused the animation
        was_paused = self.pause_play(PlotWindow.PAUSE)
        self._get_attributes()
        self.pref_popup = PreferencesWindow.PreferencesWindow(self.master, self.attributes)
        self.master.wait_window(self.pref_popup.top)
        if list(self.attributes.values()) != self.pref_popup.attributes:
            #an attribute was changed, so reassign the attributtes and relaunch
            self.attributes = dict(zip(self.attributes.keys(), self.pref_popup.attribute_values))
            self._set_attributes()
            self.launch()
        #wipe this from memory
        del self.pref_popup
        #unpause if the user was playing before the launch
        self.pause_play(was_paused)
        
    def _get_attributes(self):
        self.attributes[self.fps_str] = (1000 / self.default_interval)
        self.attributes[self.n_points_str] = self.default_points_on_line

    def _set_attributes(self):
        self.default_interval = 1000 / float(self.attributes[self.fps_str])
        self.default_points_on_line = self.attributes[self.n_points_str]


    def color_menu_create(self):
        self.color_menu.add_command(label="New start color", command=self.new_start_color)
        self.color_menu.add_command(label="New end color", command=self.new_end_color)

    def object_menu_create(self):
        self.object_menu.add_command(label="Grid", command=self.grid_popup)
        self.object_menu.add_command(label="Circle", command=self.circle_popup)
        self.object_menu.add_command(label="Disk", command=self.disk_popup)
        self.object_menu.add_command(label="Spindle", command=self.spindle_popup)
        self.object_menu.add_separator()
        self.object_menu.add_command(label="List", command=self.shape_window)
        self.object_menu.add_command(label="Remove First", command=self.remove_first)
        self.object_menu.add_command(label="Remove Last", command=self.remove_last)
        self.object_menu.add_command(label="Remove All", command=self.master_blaster)

    def help_menu_create(self):
        self.help_menu.add_command(label="View Help", command=self.help_message_box)

    def file_menu_create(self):
        self.file_menu.add_command(label="Save", command=self.save)
        self.file_menu.add_command(label="Open", command=self.open)
        self.file_menu.add_command(label="Exit", command=self.master.quit)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save as GIF", command=self.save_gif_handler)
        self.file_menu.add_command(label="Save as Video", command=self.save_video_handler)

    def new_end_color(self):
        new_end_color = self.new_color_selector_box(self.plot_object._end_color)
        self.point_grid.end_color = new_end_color
        self.end_color = new_end_color
        self.plot_object.set_end_color(new_end_color)

    def new_start_color(self):
        new_start_color = self.new_color_selector_box(self.plot_object._start_color)
        self.start_color = new_start_color
        self.point_grid.start_color = new_start_color
        self.plot_object.set_start_color(new_start_color)

    def new_color_selector_box(self, init_color=(0,0,0)):
        was_paused = self.pause_play(PlotWindow.PAUSE)
        init_color = convert_to_byte_color(init_color)
        new_color = convert_to_zero_to_one(colorchooser.askcolor(color=init_color,
                                                            title="Pick a new color")[0])
        self.pause_play(was_paused)
        return new_color

    def help_message_box(self):
        #pause the animation
        self.help_message_str = "Sam Doud needs to write this up"
        was_paused_state = self.pause_play(PlotWindow.PAUSE)
        #launch the message box
        tkinter.messagebox.showinfo("Help", self.help_message_str)
        #resume the animation if it was playing
        self.pause_play(was_paused_state)

    def save(self):
        """
        Serialize the data of the program into a pickle file defined by the user.
        """
        previous_state = self.plot_object.pause
        self.pause_play(COMPUTING)
        was_paused = self.pause_play(PlotWindow.PAUSE)
        data_dict = self.serialize()
        #get a file name from the user
        file_name = self.save_file_dialog()
        #check if the user actually defined a file
        #(i.e. didn't exit the prompt w/o selecting a file)
        if file_name:
            with open(file_name, "wb+") as save_file:
                pickle.dump(data_dict, save_file)
        self.pause_play(was_paused)
        self.pause_play(previous_state)

    def open(self):
        """
        Method to open a file that defines a previous state of the program.
        """
        was_paused = self.pause_play(PlotWindow.PAUSE)
        file_name = self.open_file_dialog()
        if not file_name:
            #user gave a non-existent name
            return
        with open(file_name, mode="rb") as open_file:
            pickle_data = pickle.load(open_file)
        #unpack this data in another method
        self.deserialize(pickle_data)
        self.launch()
        self.pause_play(was_paused)

    def break_apart_lines(self):
        """
        Take the line_collection and get the first point in the point order of every point and
        store that in a list so it can be pickled and reassembled later.
        """
        lines = self.line_collection
        lines_to_save = [list(line) for line in self.line_collection]
        for index, shape in enumerate(lines):
            line = shape[DATA]
            temp_line_list = []
            for point in line.points:
                temp_line_list.append(point.complex)
            lines_to_save[index][DATA] = temp_line_list
        return lines_to_save

    def master_blaster(self):
        """
        Deletes all objects on the graph
        """
        #pass an empty list
        self.new_lines([])
        self.point_grid.n_lines = 0

    def bring_lines_together(self, data):
        """
        Given a set of points on a line, change them into ComplexPoint and Line objects.
        Needed as these classes cannot be pickled.
        """
        shapes_in_data = list(data)
        for index, shape in enumerate(data):
            line = shape[DATA]
            temp_points_on_line = []
            for points in line:
                temp_point = ComplexPoint.ComplexPoint(points)
                temp_points_on_line.append(temp_point)
            temp_line = Line.Line("z", temp_points_on_line[0].complex,
                                    temp_points_on_line[-1].complex,
                                    len(temp_points_on_line), temp_points_on_line,
                                    start_color=self.start_color, end_color=self.end_color)
            shapes_in_data[index][DATA] = temp_line
        return shapes_in_data

    def serialize(self):
        """
        Method that handles packing and saving the data from the current homotopy.
        """
        #get the first function from the user. If it does not exist, defaults to "z"
        current_functions = self.point_grid.functions[0].function_str
        #if the user declared multiple functions, handle that below
        if len(self.point_grid.functions) > 1:
            functions_in_loop = ""
            for function in self.point_grid.functions[1:]:
                functions_in_loop += functions_in_loop + ";" + function.function_str
            current_functions += functions_in_loop
        n_steps = self.point_grid.n_steps
        id_counter = self.id_number_counter
        lines = self.break_apart_lines()
        reverse = self.reverse_checkbox_var.get()
        outlier = self.outlier_remover_var.get()
        #get the limits from the user if defined
        if all(self.fetch_limits()):
            limits = (self.point_grid.real_max, self.point_grid.real_min,
                      self.point_grid.imag_max, self.point_grid.imag_min)
        else:
            #the limits were not defininded by the user
            limits = (None, None, None, None)
        #pack the data 
        return {self.functions_pickle_str:current_functions, self.n_steps_pickle_str:n_steps,
                self.id_counter_pickle_str:id_counter, self.lines_pickle_str:lines,
                self.outlier_remover_pickle_str:outlier,
                self.reverse_checkbox_pickle_str:reverse, self.limits_pickle_str:limits}

    def save_file_dialog(self, extension=".cht"):
        """
        Prompts the user to choose a file name and directory to save their data to.
        """
        title = "Save homotopy as"
        extensions = self.extensions
        if extension is not ".cht":
            extensions[0] = ("", extension)
        file_name = filedialog.asksaveasfilename(filetypes=extensions,
                                             defaultextension=extension, title=title)
        return file_name

    def deserialize(self, pickle_data):
        """
        Take the data from the pickle and load it into the program.
        """
        self.set_checkbox(self.reverse_checkbox, self.reverse_checkbox_var,
                          pickle_data[self.reverse_checkbox_pickle_str])
        self.set_checkbox(self.outlier_remover_checkbox, self.outlier_remover_var,
                          pickle_data[self.reverse_checkbox_pickle_str])
        self.id_number_counter = pickle_data[self.id_counter_pickle_str]
        n_functions = pickle_data[self.functions_pickle_str].count(";") + 1
        self.set_text(self.n_entry,
                      str(int(((pickle_data[self.n_steps_pickle_str] - 1) / n_functions))))
        self.set_text(self.function_entry, pickle_data[self.functions_pickle_str])
        self.line_collection = self.bring_lines_together(pickle_data[self.lines_pickle_str])
        limits = pickle_data[self.limits_pickle_str]
        #the user had defined limits
        if any(limits):
            self.set_text(self.real_max_entry, limits[0])
            self.set_text(self.real_min_entry, limits[1])
            self.set_text(self.imag_max_entry, limits[2])
            self.set_text(self.imag_min_entry, limits[3])
        self.point_grid.new_lines(self.line_collection)
        self.plot_object.set_frame(0)

    def update_latex(self, a, b, c):
        try:
            self.function_display.new_input(self.function_entry.get().lower())
        except:
            return

    def set_checkbox(self, check_box, check_box_var, value):
        """
        General method to set the value of a checkbox based on a value
        """
        if check_box_var.get() == ON:
            check_box.select()
        else:
            check_box.deselect()

    def set_text(self, entry_box, text):
        """
        General method to set a text entry based on a entry object and text.
        """
        entry_box.delete(0, END)
        entry_box.insert(0, text)

    def open_file_dialog(self, extension=".cht"):
        """
        Launches a file browser that prompts the user to select a file to load.
        """
        title = "Open homotopy data"
        extensions = self.extensions
        if extension is not ".cht":
            extensions[0] = ("", extension)
        file_name = filedialog.askopenfilename(filetypes=extensions,
                                             defaultextension=extension, title=title)
        return file_name

    def create_frames(self):
        common_bd = 0
        self.plotting_frame = Frame(self.master, bd=common_bd)
        self.utility_frame = Frame(self.master, bd=common_bd)
        self.toolbar_frame = Frame(self.plotting_frame)

    def grid_frames(self):
        self.plotting_frame.grid(row=0, column=0, columnspan=self.size)
        self.toolbar_frame.grid(row=self.slider_row + 2, column=0, columnspan=self.size)
        self.utility_frame.grid(row=self.slider_row + 1, column=0, columnspan=self.size - 1)
        #self.function_display_frame.grid(row=self.slider_row + 1, column=self.size)


    def create_widgets(self):
        """
        Creates and arranges the GUI.
        """
        common_width = 5
        common_bd = 3
        #checkbox to control outlier logic
        self.go_to_first_frame_button = Button(self.toolbar_frame, image=self.go_to_domain_icon,
                                               command=self.go_to_first_frame)
        self.frame_decrement_button = Button(self.toolbar_frame, image=self.frame_decrement_icon,
                                             command=self.decrement_frame)
        self.pause_play_button = Button(self.toolbar_frame, image=self.play_icon,
                                        command=self.pause_play_button_flip)
        self.frame_increment_button = Button(self.toolbar_frame, image=self.frame_increment_icon,
                                             command=self.increment_frame)
        self.zoom_in_button = Button(self.toolbar_frame, image=self.zoom_in_icon,
                                     command=self.zoom_in_step)
        self.zoom_out_button = Button(self.toolbar_frame, image=self.zoom_out_icon,
                                      command=self.zoom_out_step)
        self.go_to_last_frame_button = Button(self.toolbar_frame, image=self.go_to_range_icon,
                                              command=self.go_to_last_frame)
        self.save_video = Button(self.toolbar_frame, image=self.save_movie_icon,
                                 command=self.save_video_handler)
        self.save_gif = Button(self.toolbar_frame, image=self.save_gif_icon,
                               command=self.save_gif_handler)
        self.function_entry = Entry(self.utility_frame, width=30, bd=common_bd, textvariable=self.function_str)
        self.function_label = Label(self.utility_frame, text="Enter a f(z)")
        self.n_label = Label(self.utility_frame, text="Number of steps")
        self.n_entry = Entry(self.utility_frame, width=common_width, bd=common_bd)
        self.submit = Button(self.utility_frame, text="Submit", command=self.launch_wrapper)
        self.outlier_remover_checkbox = Checkbutton(self.utility_frame, text="Remove outliers",
                                                    variable=self.outlier_remover_var,
                                                    onvalue=ON, offvalue=OFF, height=1, width=12)
        self.reverse_checkbox = Checkbutton(self.utility_frame, text="Reverse",
                                            variable=self.reverse_checkbox_var,
                                            onvalue=ON, offvalue=OFF, height=1, width=6)
        self.pop_from_collection = Button(self.utility_frame, text="Remove last",
                                          command=self.remove_last)
        self.pause_play_label = Label(self.utility_frame, text="Awaiting function")
        self.frame_slider = Scale(self.master, from_=0, to=1, orient=HORIZONTAL,
                                  command=self.go_to_frame_slider)        
        self.real_max_label = Label(self.utility_frame, text="Real max")
        self.real_min_label = Label(self.utility_frame, text="Real min")
        self.imag_max_label = Label(self.utility_frame, text="Imag max")
        self.imag_min_label = Label(self.utility_frame, text="Imag min")
        self.real_max_entry = Entry(self.utility_frame, width=common_width, bd=common_bd)
        self.real_min_entry = Entry(self.utility_frame, width=common_width, bd=common_bd)
        self.imag_min_entry = Entry(self.utility_frame, width=common_width, bd=common_bd)
        self.imag_max_entry = Entry(self.utility_frame, width=common_width, bd=common_bd)
        self.function_display_canvas = FigureCanvasTkAgg(self.function_display.fig, master=self.utility_frame)

    def grid_widgets_in_frames(self):
        """Method to pack widgets created in above method onto the window.
        This method only exists for organization purposes.
        Pythonically, this code is probably bad. I am referencing variables that are created
        outside of this method but not in the __init__ method."""
        self.function_label.grid(row=0, column=0)
        self.function_entry.grid(row=0, column=1, columnspan=3)
        self.n_entry.grid(row=1, column=1)
        self.n_label.grid(row=1, column=0)
        self.outlier_remover_checkbox.grid(row=2, column=3)
        self.reverse_checkbox.grid(row=2, column=4)
        self.submit.grid(row=0, column=4)
        self.pause_play_label.grid(row=2, column=1)
        self.redraw_slider(1)
        #pack into frame toolbar
        self.go_to_first_frame_button.pack(side=LEFT)
        self.frame_decrement_button.pack(side=LEFT)
        self.pause_play_button.pack(side=LEFT)
        self.frame_increment_button.pack(side=LEFT)
        self.go_to_last_frame_button.pack(side=LEFT)
        self.zoom_in_button.pack(side=LEFT)
        self.zoom_out_button.pack(side=LEFT)
        self.save_gif.pack(side=LEFT)
        self.save_video.pack(side=LEFT)
        self.function_display_canvas.get_tk_widget().grid(row=0, column=5,
                                                          columnspan=self.function_display.column_size,
                                                          rowspan=self.function_display.row_size)

    def redraw_slider(self, steps):
        """Need to recreate the frame slider if the number of steps change.
        All this method does is destroys the old slider, create a new one with the current number
        of steps, and then reinject it to its old spot."""
        self.frame_slider.destroy()
        self.frame_slider = Scale(to=self.point_grid.n_steps - 1, length=(self.size * 100),
                                  from_=0, orient=HORIZONTAL, command=self.go_to_frame_slider,)
        self.frame_slider.grid(row=self.slider_row, column=self.slider_column)

    def go_to_frame_slider(self, event):
        """Get the value from the slider if the user changes it and set the frame equal to that."""
        self.plot_object.frame_number = self.frame_slider.get()

    def set_slider(self, frame_number):
        """
        Take the frame number passed and set the frame slider to it
        This method is accessed by the observer in the PlotWindow.
        """
        self.frame_slider.set(frame_number)

    def add_to_collection(self, lines, center=None, type_str=None):
        """Adds a set of lines to the collection and appends a id tag"""
        self.line_collection.append((lines, self.id_number_counter, center, type_str))
        self.point_grid.new_lines(self.line_collection)
        #increment the id tag
        self.id_number_counter += 1
        #return the id tag less one (as to refer to this object)
        #try:
        #    if self.plot_object.anim:
        #        pass
        #except AttributeError:
        #    try:
        #        self.plot_object.animate()
        #    except AttributeError:
        #        pass
        return self.id_number_counter - 1

    def remove_last(self, id_number=None, top=False):
        """Removes a line collection from the list. If no index is passed, the collection is
        treated like a stack."""
        #search for the line
        #This is an ordered set. Using a binary search
        #did the user pass a value for id_number?
        if top:
            #user wants the first element removed
            self.line_collection.pop(0)
        else:
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
                except IndexError:
                    return False
            else:
                #user did not pass an id number. pop from top of stack
                if self.line_collection:
                    self.line_collection.pop()
                else:
                    return False
        if self.line_collection:
            self.point_grid.new_lines(self.line_collection)

        self.relaunch()
        #start the animation back up
        return True

    def remove_first(self):
        """Take the first item on the collection and remove it.
        Then recalculate the graph."""
        self.remove_last(top=True)

    def build_sample(self):
        """A sampler method to test adding and removing shapes."""
        self.build_circle(1, complex(1, 1))
        self.build_grid(complex(-1, 1), complex(1, -1), 10)

    def flattened_lines(self):
        """
        The collection of lines is a list of tuples with
        each tuple containing a list of lines and an id.
        This method takes all the lines in the collection
        and returns them as one list.
        """
        stripped_of_id = [line[0] for line in self.line_collection]
        return [item for sublist in stripped_of_id for item in sublist]

    def add_lines(self, list_of_lines, center=None, type_str=None):
        """
        Given a list of lines, add them to the Plot.
        """
        id = self.add_to_collection(list_of_lines, center, type_str)
        if self.animating_already:
            self.relaunch()
        return id

    def new_lines(self, list_of_new_lines, reanimate=False):
        """Replace the old set of lines with a new one.
        IDs will be reassigned starting at zero."""
        #location of the ID element in the line
        id_index = 1
        #go through each line object and reassign the ID
        for id_tag in range(len(list_of_new_lines)):
            list_of_new_lines[id_tag] = change_tuple_value(list_of_new_lines[id_tag],
                                                           id_index, id_tag)
        #replace the line collection
        self.line_collection = list_of_new_lines
        self.point_grid.new_lines(list_of_new_lines)
        #force the object to square itself
        self.point_grid.force_square()
        #relaunch the animation
        if reanimate:
            self.relaunch()

    def build_circle(self, radius, center=complex(0, 0)):
        """
        Build a circle from a popup
        """
        return self.add_lines(self.point_grid.circle(radius, center, self.default_points_on_line),
                              center, self.type_strs["circle"])

    def build_grid(self, upper_right, lower_left, lines_num, color=None):
        """
        Build a grid from a popup.
        """
        #if not start_color:
        #    start_color = self.start_color
        #    end_color = self.end_color
        #    color_diff = self.color_diff
        center = complex((upper_right.real + lower_left.real / 2),
                         (upper_right.imag + lower_left.imag / 2))
        return self.add_lines(self.point_grid.grid_lines(upper_right,
                                                         lower_left, lines_num,
                                                         self.default_points_on_line), center,
                              self.type_strs["grid"])

    def build_disk(self, radius, n_circles, center):
        return self.add_lines(self.point_grid.disk(radius, n_circles, center),
                              center, self.type_strs["disk"])       

    def build_spindle(self, n_roots_of_unity, radius=1, n_circles=1, center=complex(0,0)):
        x = (self.point_grid.draw_roots_of_unity_spindle(n_roots_of_unity, n_circles, radius,
                                                         center),
             center, self.type_strs["spindle"])
        return self.add_lines(*x)
    
    def save_video_handler(self):
        """Dispatches the Plot to save the video."""
        #now actually save the graph
        old_state = self.pause_play(COMPUTING)
        if self.plot_object.install_ffmpeg:
            self.alert_ffmpeg()
            return
        file_name = self.save_file_dialog(".mp4")
        #check if the user actually defined a file
        #(i.e. didn't exit the prompt w/o selecting a file)
        if file_name:
            self.plot_object.save(video=True, frames=(1000 / self.default_interval),
                                  path=file_name)
        self.pause_play(old_state)

    def save_gif_handler(self):
        """Dispatches the Plot to save a GIF."""
        #now actually save the graph
        old_state = self.pause_play(COMPUTING)
        #if self.plot_object.install_ffmpeg:
        #    self.alert_ffmpeg()
        #    return
        file_name = self.save_file_dialog(extension=".gif")
        #check if the user actually defined a file
        #(i.e. didn't exit the prompt w/o selecting a file)
        if file_name:
            self.plot_object.save(gif=True, frames=(1000 / self.default_interval), path=file_name)
        self.pause_play(old_state)

    def alert_ffmpeg(self):
        messagebox.askquestion(title="ffmpeg not found",
                               message="In order to perform this operation ffmpeg must be installed and the command 'ffmpeg' must execute")

    def launch_wrapper(self, entry=None):
        self.animating_already_secondary = True
        self.launch()
        self.master.update()

    def launch(self, entry=None):
        """
        Create a new animation based on the data given by the user.
        This method will be called on the press of the submit button.
        """
        recently_activated = False
        if self.animating_already:
            self.pause_play(COMPUTING)
            self.master.update()
        #take the focus off of any entry
        self.master.focus()
        #take the input from the user.. if its null, set ito the identity function
        self.point_grid.set_user_limits(self.fetch_limits())
        if self.function_entry.get():
            self.function_objects = []
            function_strings = str(self.function_entry.get()).split(';') #split by the semi-colon
            for function_string in function_strings:
                #add each passed string to the list of functions
                try:
                    #check if the fuction is valid
                    function_object = func.ComplexFunction(function_string.strip())
                except Exception:
                    #fallback to the identity function
                    function_object = self.identity_function
                #add the user or identity function to the function stack
                self.function_objects.append(function_object)
        else:
            #fallback to identity if no string is provided
            self.function_objects = [self.identity_function]
        try:
            #see if the user supplied a number of steps.
            steps_from_user = int(self.n_entry.get()) + 1
        except Exception:
            steps_from_user = 1 #no animation
        self.n_steps_per_function = steps_from_user
        #get if the user has checked the reverse animation box
        self.set_checkbox_vars()
        #give the point grid its function
        self.point_grid.provide_function(self.function_objects, steps_from_user,
                                         reverse=self.reverse,
                                         remove_outliers=self.remove_outliers)
        self.redraw_slider(self.point_grid.n_steps)
        #code for if this is the initial run of the launch method
        #prevents the application from launching unneeded windows
        #bind the method set_slider to the plot_object
        if not self.animating_already:
            self.animating_already = True
            self.plot_object = PlotWindow.PlotWindow(self.point_grid)
            self.plot_object.bind(self.set_slider)
            #now we can bind the keys
            self.key_bindings()
            self.update_graph()
        else:
            #call on the animator to start at the beginning of the graph
            self.plot_object.set_frame(0)
            #pass an iterable to reorder the frames
            self.plot_object.anim.frame_seq = cycle(range(self.point_grid.n_steps))
        #allows the color computation to deal with if the animation is reversing
        self.plot_object.reverse = self.reverse
        #set the boolean that controls the outlier operation in the pointgrid to that of the user
        self.redraw_limits()
        self.pause_play(PLAY_FLAG)

    def set_checkbox_vars(self):
        self.reverse = self.reverse_checkbox_var.get() == ON
        self.remove_outliers = self.outlier_remover_var.get() == ON

    def redraw_limits(self):
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
            all_clear = False
        else:
            if real_max <= real_min or imag_max <= imag_min:
                all_clear = False
        if all_clear:
            return limits
        else:
            #this is a bad implementation. Just an empty four-tuple if there are no limits
            return (None, None, None, None)

    def get_limit_from_entry(self, limit_entry):
        """
        Given a limit entry, determine its value if it is a number.
        """
        #check if the use passed something legal
        #remove any complex notation
        num = limit_entry.get().replace("j", "")
        try:
            return float(num)
        except:
            return None

    def update_graph(self):
        """
        Create the frame on which the matplotlib figure will be displayed.
        Also, kick off the animation.
        """
        self.canvas = FigureCanvasTkAgg(self.plot_object.fig, master=self.plotting_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=self.size)
        self.toolbar = NavigationBar.NavigationBar(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        #self.plot_object.fig.canvas.mpl_connect('button_press_event', self.toggle_pause)
        #self.canvas.show()
        #self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        del self.animation_thread
        self.animation_thread = threading.Thread(target=self.plot_object.animate,
                                                 args=(self.default_interval,))
        self.animation_thread.start()
        
    def spindle_popup(self):
        self.general_popup(BuilderWindows.SpindleBuilderPopup, self.build_spindle)

    def disk_popup(self):
        self.general_popup(BuilderWindows.DiskBuilderPopup, self.build_disk)

    def circle_popup(self):
        """
        Launch the circle popup window, then build the circle from the prompt.
        """
        self.general_popup(BuilderWindows.CircleBuilderPopup, self.build_circle)

    def grid_popup(self):
        """
        Launch a pop-up window to build a user-defined grid, then build that grid from the prompt.
        """
        self.general_popup(BuilderWindows.GridBuilderPopup, self.build_grid)

    def general_popup(self, popup_class, popup_function):
        was_paused = self.pause_play(PlotWindow.PAUSE)
        self.popup_window = popup_class(self.master)
        self.master.wait_window(self.popup_window.top)
        data = self.popup_window.data
        #try:
        #    #go to the popup function with the unpacked tuple arg
        #    popup_function(*data)
        #except:
        #    print("invalid data")
        popup_function(*data)
        #remove from memory
        self.popup_window = None
        self.pause_play(was_paused)

    def relaunch(self):
        """Something has changed in the data, realunch the plot to reflect that."""
        self.pause_play(COMPUTING)
        self.master.update()
        self.point_grid.provide_function(self.point_grid.functions, self.n_steps_per_function,
                                         reverse=self.reverse,
                                         remove_outliers=self.remove_outliers)
        self.pause_play(PLAY_FLAG)
        self.redraw_limits()
        self.master.update()

    def shape_window(self):
        """Launch a window that shows a list of the current shapes.
           User can remove lines if desired."""
        was_paused = self.pause_play(PlotWindow.PAUSE)
        self.popup_window = ShapesMenu.ShapesMenu(self.master, self.line_collection)
        #wait for the window to close
        self.master.wait_window(self.popup_window.top)
        temp_ln_coll = [line for line in self.line_collection if line[1] in self.popup_window.ids]
        if self.line_collection != temp_ln_coll:
            #checked if the lists are different
            self.new_lines(temp_ln_coll, True)
        self.popup_window = None
        self.pause_play(was_paused)


def resource_path(relative_path):
    """
    A function that gets the absolute path from relative. Needed for redist.
    Found from StackOverflow.
    http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    user: Max
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def change_tuple_value(tuple_item, index_to_replace, value_to_use):
    """Replace a tuple's value at a specified index"""
    return tuple(tuple_item[:index_to_replace] + (value_to_use, )
                + tuple_item[index_to_replace + 1:])

def is_properly_ordered(real_max, real_min, imag_max, imag_min):
    """Determines if a set of limits on the complex plane is legal.
    That is to say that all maximums are strictly greater than their minimums."""
    return real_max > real_min and imag_max > imag_min


ROOT = Tk()
WINDOW = Application(master=ROOT)
WINDOW.mainloop()
