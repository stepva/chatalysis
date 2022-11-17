import tkinter as tk
from typing import Any

from tabulate import tabulate


class WindowTopTen(tk.Toplevel):
    """Window showing the top 10 individual conversations & top 5 group chats"""

    def __init__(self, program: Any):
        tk.Toplevel.__init__(self)
        self.Program = program

        self.title("Top conversations")
        self.geometry("600x600")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label_analyzing = tk.Label(self, text="Analyzing...")
        self.label_error: tk.Label | None = None
        self.label_top: tk.Label | None = None

        self.show_top()  # runs the top 10 analysis & print

    def show_top(self) -> None:
        """Analyzes and shows the top conversations"""
        # Calculate the top conversations if not done already
        if self.Program.top_ten_individual is None:
            self.label_analyzing.grid(column=0, row=0, padx=5, pady=5)
            self.update()

            topIndividual, topGroup = self.Program.source.top_ten()

            self.Program.top_ten_individual = tabulate(
                topIndividual, headers=["Conversation", "Messages"], colalign=("left", "right")
            )

            if len(topGroup) > 0:
                self.Program.top_five_groups = tabulate(
                    topGroup, headers=["Conversation", "Messages"], colalign=("left", "right")
                )
            else:
                self.Program.top_five_groups = "No group chats available"

        self.label_analyzing.destroy()

        # Print the top conversation, fixed font is necessary for the correct table formatting done by tabulate
        self.label_top = tk.Label(
            self,
            text="\n".join(
                [
                    "Top 10 individual conversations\n",
                    self.Program.top_ten_individual,
                    "\n",
                    "Top 5 group chats\n",
                    self.Program.top_five_groups,
                ]
            ),
            anchor="n",
            font=("TkFixedFont",),
        )
        self.label_top.grid(column=0, row=0)
