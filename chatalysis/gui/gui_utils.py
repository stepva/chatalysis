import traceback
import tkinter as tk
from tkinter import messagebox


def show_error(window: tk.Tk | tk.Toplevel, err_message: str, print_stacktrace: bool) -> None:
    """Shows an error and places the last open GUI window back on top

    :param window: last open GUI window
    :param err_message: error message to display
    :param print_stacktrace: bool whether to print stacktrace of the error or not
    """
    if print_stacktrace:
        messagebox.showerror("Error", f"{err_message}\n\n{traceback.format_exc()}")
    else:
        messagebox.showerror("Error", err_message)
    window.lift()
