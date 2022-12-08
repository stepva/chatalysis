import abc
import tkinter as tk


class SingletonWindow(tk.Toplevel):
    """Non-resizable GUI window with a singleton behavior"""

    def __init__(self) -> None:
        tk.Toplevel.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.resizable(False, False)

    @abc.abstractmethod
    def _close(self) -> None:
        """Window destructor, which closes the window and resets the references
        to this instance in other classes"""
