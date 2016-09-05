import tkinter
from tkinter import Entry, Label, Button, Toplevel, messagebox

class GridLinesWindow(object):
    """Gets the user's preference of grid lines."""

    def __init__(self, master):
        self.top = Toplevel(master)
        self.entry_width = 15
        self.set_none_limits()
        self.real_spacing_label = Label(self.top, text="Real axis spacing: ")
        self.imag_spacing_label = Label(self.top, text="Imag axis spacing: ")
        self.real_spacing_entry = Entry(self.top, width=self.entry_width)
        self.imag_spacing_entry = Entry(self.top, width=self.entry_width)
        self.submit_button = Button(self.top, text="Submit", command=self.submit)
        self.cancel_button = Button(self.top, text="Cancel", command=self.top.destroy)
        self.real_spacing_label.grid(row=0, column=0)
        self.imag_spacing_label.grid(row=1, column=0)
        self.real_spacing_entry.grid(row=0, column=1)
        self.imag_spacing_entry.grid(row=1, column=1)
        self.submit_button.grid(row=2, column=0)
        self.cancel_button.grid(row=2, column=1)
        self.top.bind("<Return>", self.submit)
        self.top.bind("<Escape>", self.top.destroy)
        self.real_spacing_entry.focus()
        
    def set_none_limits(self):
        self.data = (None, None)

    def submit(self, event=None):
        legal = True
        try:
            imag_spacing = float(self.imag_spacing_entry.get())
            real_spacing = float(self.real_spacing_entry.get())
            if not str(self.imag_spacing).isdecimal() and self.imag_spacing <= 0:
                self.imag_spacing_entry.config(text="", bg="red")
                legal = False
                self.illegal_entry("Imag")
            else:
                self.imag_spacing_entry.config(bg="white")
            if not str(self.real_spacing).isdecimal() and self.real_spacing <= 0:
                self.real_spacing_entry.config(text="", bg="red")
                legal = False
                self.illegal_entry("Real")
            else:
                self.imag_spacing_entry.config(bg="white")
            if legal:
                self.data = (real_spacing, imag_spacing)
                self.top.destroy()
        except TypeError:
            print("Values passed are not real numbers")

    def illegal_entry(self, type):
        tkinter.messagebox.Message(type + " spacing must be a positive number.")