import os
import sys
import tkinter
from tkinter import *

from PIL import ImageTk,Image

import gui
from home import Home
from history import Hist

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class Nav:
    def __init__(self, window):
        self.window = window

    def switch(self, ind, page):
        for child in self.options_fm.winfo_children():
            if isinstance(child, Label):
                child['bg'] = '#000000'
        ind['bg'] = '#5D0D0D'

        for fm in self.main_fm.winfo_children():
            fm.destroy()
            self.new_window.update()

        page()

    def home_page(self):
        Home(self.main_fm)

    def help_page(self):
        self.help_page_fm = Frame(self.main_fm)
        self.help_page_fm.pack(fill=BOTH, expand=True)
        image = Image.open(resource_path(r'.\assets\frame0\help.png'))

        # Resize the image
        # image = image.resize((1000, 200))  # Resize to fit your needs

        # Convert the image to PhotoImage
        photo = ImageTk.PhotoImage(image)

        # Create a label to hold the image
        label = Label(self.help_page_fm, image=photo)
        label.image = photo  # keep a reference to the image!

        # Place the label at a specific position
        label.place(x=0, y=0, width=1000, height=540)

    def health_page(self):
        self.health_page_fm = Frame(self.main_fm)
        self.health_page_fm.pack(fill=BOTH, expand=True)
        image = Image.open(resource_path(r'.\assets\frame0\health.png'))

        # Resize the image
        image = image.resize((1000, 540))  # Resize to fit your needs

        # Convert the image to PhotoImage
        photo = ImageTk.PhotoImage(image)

        # Create a label to hold the image
        label = Label(self.health_page_fm, image=photo)
        label.image = photo  # keep a reference to the image!

        # Place the label at a specific position
        label.place(x=0, y=0, width=1000, height=540)


    def hist_page(self):
        Hist(self.main_fm)

    def close_new_page(self, new_window):
        gui.SessionManager.logout()
        new_window.destroy()  # This will close the new window
        self.window.deiconify()

    def open_new_page(self):
        self.new_window = Toplevel(self.window, background='#000000')
        self.new_window.title("New Page")
        self.new_window.geometry("1000x550")

        # Back button that closes the new window
        # back_button.pack(pady=20)

        self.options_fm = tkinter.Frame(self.new_window, bg='#000000')
        options_fm = self.options_fm

        home_btn = Button(options_fm, text="Home", command=lambda: self.switch(home_ind,page=self.home_page),
                          bd=0, fg='#FFFFFF', activebackground='#000000', bg="#000000", cursor='hand2')
        home_btn.place(x=0, y=0, width=125, height=35)
        home_ind = Label(options_fm, bg='#5D0D0D')
        home_ind.place(x=22, y=32, width=80, height=10)

        hist_btn = Button(options_fm, text="History", command=lambda: self.switch(hist_ind,page=self.hist_page),
                          bd=0, fg='#FFFFFF', activebackground='#000000', bg="#000000", cursor='hand2')
        hist_btn.place(x=125, y=0, width=125, height=35)
        hist_ind = Label(options_fm, bg='#000000')
        hist_ind.place(x=22 + 125, y=32, width=80, height=10)

        back_btn = Button(options_fm, text="Logout", command=lambda: self.close_new_page(self.new_window),
                          bd=0, fg='#FFFFFF', activebackground='#000000', bg="#000000", cursor='hand2')
        back_btn.place(x=890, y=0, width=125, height=35)
        back_ind = Label(options_fm, bg='#000000')
        back_ind.place(x=910, y=32, width=80, height=10)

        help_btn = Button(options_fm, text="Help", command=lambda: self.switch(help_ind,self.help_page),
                          bd=0, fg='#FFFFFF', activebackground='#000000', bg="#000000", cursor='hand2')
        help_btn.place(x=890 - 125, y=0, width=125, height=35)
        help_ind = Label(options_fm, bg='#000000')
        help_ind.place(x=910 - 125, y=32, width=80, height=10)

        health_btn = Button(options_fm, text="Health", command=lambda: self.switch(health_ind, self.health_page),
                          bd=0, fg='#FFFFFF', activebackground='#000000', bg="#000000", cursor='hand2')
        health_btn.place(x=125+125, y=0, width=125, height=35)
        health_ind = Label(options_fm, bg='#000000')
        health_ind.place(x=22+125+125, y=32, width=80, height=10)

        options_fm.pack(pady=5)
        options_fm.pack_propagate(False)
        options_fm.configure(width=1000, height=35)

        self.main_fm = tkinter.Frame(self.new_window, bg='#000000')
        self.main_fm.pack(fill=BOTH, expand=True)

        self.home_page()
