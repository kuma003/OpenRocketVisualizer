"""dialogs.py"""

import tkinter
import tkinter.filedialog

import pygame as pg


def open_ork_file():
    """Open file dialog and return the file name"""
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(
        parent=top, filetypes=[("OpenRocket Files", "*.ork")]
    )
    top.destroy()
    # NOTE: Clear event queue to avoid double file open event occurred(ad hoc). That is why other event (e.g. QUIT) does not work.
    pg.event.clear()
    return file_name


def ask_whether_to_exit():
    """Ask whether to exit the application"""
    top = tkinter.Tk()
    top.withdraw()  # hide window
    res = tkinter.messagebox.askyesno("Exit", "Do you want to exit?")
    top.destroy()
    # NOTE: Clear event queue to avoid double file open event occurred(ad hoc). That is why other event (e.g. QUIT) does not work.
    pg.event.clear()
    return res
