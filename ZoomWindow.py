import tkinter
from tkinter import Entry, Label, Button, Toplevel, StringVar

class ZoomWindow(object):
    """description of class"""

    def __init__(self, master):
        self.top = Toplevel(master)
        self.entry_width = 15
        self.set_none_limits()
        self.real_max_label = Label(self.top, text="Real Max: ")
        self.real_min_label = Label(self.top, text="Real Min: ")
        self.imag_max_label = Label(self.top, text="Imag Max: ")
        self.imag_min_label = Label(self.top, text="Imag Min: ")
        self.real_max_entry = Entry(self.top, width=self.entry_width)
        self.real_min_entry = Entry(self.top, width=self.entry_width)
        self.imag_max_entry = Entry(self.top, width=self.entry_width)
        self.imag_min_entry = Entry(self.top, width=self.entry_width)
        self.submit_button = Button(self.top, text="Submit", command=self.submit)
        self.cancel_button = Button(self.top, text="Cancel", command=self.top.destroy)
        self.real_max_label.grid(row=0, column=0)
        self.real_min_label.grid(row=1, column=0)
        self.imag_max_label.grid(row=2, column=0)
        self.imag_min_label.grid(row=3, column=0)
        self.real_max_entry.grid(row=0, column=1)
        self.real_min_entry.grid(row=1, column=1)
        self.imag_max_entry.grid(row=2, column=1)
        self.imag_min_entry.grid(row=3, column=1)
        self.submit_button.grid(row=4, column=0)
        self.cancel_button.grid(row=4, column=1)
        self.top.bind("<Return>", self.submit)
        self.top.bind("<Escape>", self.top.destroy)
        self.real_max_entry.focus()
        
    def set_none_limits(self):
        self.imag_min, self.imag_max, self.real_max, self.real_min = (None, None, None, None)

    def submit(self, event=None):
        try:
            self.imag_min = float(self.imag_min_entry.get())
            self.imag_max = float(self.imag_max_entry.get())
            self.real_min = float(self.real_min_entry.get())
            self.real_max = float(self.real_max_entry.get())
            if self.imag_min > self.imag_max or self.real_min > self.real_max:
                self.set_none_limits()
                print("A min field exceeds a max field")
        except TypeError:
            print("Values passed are not real numbers")
        self.top.destroy()


