from __future__ import annotations
from typing import Any, TYPE_CHECKING
from tkinter import ttk

from gui.singleton_window import SingletonWindow
from tabulate import tabulate

if TYPE_CHECKING:
    from gui.main_gui import MainGUI


class WindowTopTen(SingletonWindow):
    """Window showing the top 10 individual conversations & top 5 group chats"""

    def __init__(self, program: Any, main_gui: MainGUI):
        SingletonWindow.__init__(self)
        self.Program = program
        self.main_gui = main_gui
        self.main_gui.window_top_ten = self

        self.title("Top conversations")
        self.geometry("600x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = ttk.Label(self, text="")
        self.show_top()  # runs the top 10 analysis & print

    def show_top(self) -> None:
        """Analyzes and shows the top conversations"""
        # Calculate the top conversations if not done already
        self.label.config(text="Analyzing...")
        self.label.grid(column=0, row=0)
        self.update()

        top_individual, top_group = self.Program.source.top_ten()

        top_individual = tabulate(top_individual, headers=["Conversation", "Messages"], colalign=("left", "right"))
        if len(top_group) > 0:
            top_group = tabulate(top_group, headers=["Conversation", "Messages"], colalign=("left", "right"))
        else:
            top_group = "No group chats available"

        # Print the top conversation, fixed font is necessary for the correct table formatting done by tabulate
        self.label.config(
            text="\n".join(
                ["Top 10 individual conversations\n", top_individual, "\n", "Top 5 group chats\n", top_group]
            ),
            justify="center",
            font=("TkFixedFont",),
        )

    def _close(self) -> None:
        self.main_gui.window_top_ten = None
        self.destroy()
