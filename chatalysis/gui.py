# Standard library imports
import os
import abc
import ctypes
import tkinter as tk
from tkinter import filedialog

# Application imports
from messenger import FacebookMessenger

# Third party imports
from tabulate import tabulate


class Window(tk.Tk):
    """Tkinter window base class"""

    def __init__(self):
        tk.Tk.__init__(self)

    @abc.abstractmethod
    def display_error(self, errorMessage: str):
        """Displays an error message in the window

        :param errorMessage: message to be displayed
        """
        pass

    @staticmethod
    def remove_labels(labels: "list[tk.Label]"):
        """Removes labels from a given window

        :param labels: list of labels to remove
        """
        for label in labels:
            if label is not None:
                label.destroy()


class MainGUI(Window):
    """Main GUI for the program"""

    def __init__(self, program):
        Window.__init__(self)
        self.label_error = None
        self.Program = program
        self.create()

    def create(self):
        """Creates the GUI widgets and renders them"""
        # fix high DPI blurriness on Windows 10
        if os.name == "nt":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            self.tk.call("tk", "scaling", 1.75)

        self.title("Chatalysis")
        self.geometry("800x300")

        # Configure grids & columns
        self.grid_columnconfigure(0, weight=1)
        for i in range(2, 5):
            self.grid_rowconfigure(i, weight=1)

        # Create buttons
        self.button_select_dir = tk.Button(self, text="Select directory", command=self.select_dir)
        self.button1 = tk.Button(self, text="Show top conversations", command=lambda: WindowTopTen(self.Program, self))
        self.button2 = tk.Button(
            self, text="Analyze individual conversations", command=lambda: WindowIndividual(self.Program, self)
        )

        # Create labels
        self.label_error = tk.Label(self, text="", fg="red", wraplength=650)
        self.label_select_dir = tk.Label(self, text="Please select directory with the messages:")

        # Create entry widgets
        self.data_dir_path_tk = tk.StringVar()
        self.entry_data_dir = tk.Entry(self, textvariable=self.data_dir_path_tk, width=60)
        self.entry_data_dir.config(background="#f02663")  # display directory path in red until a valid path is entered

        # Render objects onto a grid
        self.label_select_dir.grid(column=0, row=0, padx=5, pady=5)
        self.button_select_dir.grid(column=0, row=1, padx=5, pady=5)
        self.entry_data_dir.grid(column=0, row=2, sticky="N", padx=5, pady=5)
        self.button1.grid(column=0, row=3, sticky="S", padx=5, pady=5)
        self.button2.grid(column=0, row=4, sticky="N", padx=5, pady=5)
        self.label_error.grid(column=0, row=5, padx=5, pady=5)

    def display_error(self, errorMessage: str):
        self.label_error.config(text=errorMessage, fg="red")

    def select_dir(self):
        """Selects directory with the data using a dialog window"""
        self.Program.data_dir_path = filedialog.askdirectory(title="Select source directory", initialdir=os.getcwd())
        self.data_dir_path_tk.set(self.Program.data_dir_path)

        try:
            self.Program.source = FacebookMessenger(self.Program.data_dir_path)
        except Exception as e:
            # directory is not valid (missing 'messages' folder or other issue)
            self.entry_data_dir.config(background="#f02663")  # display directory path in red
            self.Program.valid_dir = False
            self.display_error(e)
            return

        self.Program.valid_dir = True
        self.label_error.config(text="")
        self.entry_data_dir.config(background="#17850b")  # display directory path in green


class WindowTopTen(Window):
    """Window showing the top 10 individual conversations & top 5 group chats"""

    def __init__(self, program, gui: MainGUI):
        if not program.valid_dir:
            # don't do anything if source directory is invalid to avoid errors
            gui.display_error("Cannot analyze until a valid directory is selected")
            return

        self.Program = program

        Window.__init__(self)
        self.title("Top conversations")
        self.geometry("600x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.labelAnalyzing = tk.Label(self, text="Analyzing...")
        self.label_error = None
        self.label_top = None

        self.show_top()  # runs the top 10 analysis & print

    def display_error(self, errorMessage: str):
        self.remove_labels([self.label_error])

        self.label_error = tk.Label(self, text=errorMessage, wraplength=650, fg="red")
        self.label_error.grid(column=0, row=1, padx=5, pady=5)

    def show_top(self):
        """Analyzes and shows the top conversations"""
        # Calculate the top conversations if not done already
        if self.Program.top_ten_individual is None:
            self.labelAnalyzing.grid(column=0, row=0, padx=5, pady=5)
            self.update()

            topIndividual, topGroup = self.Program.source.top_ten()

            self.Program.top_ten_individual = tabulate(
                topIndividual.items(), headers=["Conversation", "Messages"], colalign=("left", "right")
            )

            self.Program.top_five_groups = tabulate(
                topGroup.items(), headers=["Conversation", "Messages"], colalign=("left", "right")
            )

        self.remove_labels([self.labelAnalyzing])  # remove the "Analyzing..." label if present

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


class WindowIndividual(Window):
    def __init__(self, program, gui: MainGUI):
        if not program.valid_dir:
            # don't do anything if source directory is invalid to avoid errors
            gui.display_error("Cannot analyze until a valid directory is selected")
            return

        self.Program = program

        Window.__init__(self)
        self.title("Analyze individual conversations")
        self.geometry("600x200")
        self.create()

    def create(self):
        """Creates and renders the objects in the window"""

        self.grid_columnconfigure(0, weight=1)
        for i in range(0, 2):
            self.grid_rowconfigure(i, weight=1)

        self.label_instructions = tk.Label(
            self,
            text="Please enter conversation name in the format 'namesurname' without special characters (for example: johnsmith)",
            wraplength=450,
        )

        # add an invisible label so that the labels indicating success or error stay in the same place
        # the entire time without the rest of the objects "jumping" around
        self.label_under = tk.Label(self, text="", wraplength=650, fg="red")

        # Entry for entering the conversation name. It's bound to start the analysis when the user hits Enter.
        self.entry_name = tk.Entry(self, width=50)
        self.entry_name.bind("<Return>", self.analyze_individual)

        self.label_instructions.grid(column=0, row=0, sticky="S", padx=5, pady=5)
        self.entry_name.grid(column=0, row=1, sticky="N", padx=5, pady=5)
        self.label_under.grid(column=0, row=2, padx=5, pady=5)

    def display_error(self, errorMessage: str):
        self.label_under.config(text=errorMessage, fg="red")

    def analyze_individual(self, _event):
        """Analyzes an individual conversation and prints information about the process"""
        self.label_under.config(text="Analyzing...", fg="black")
        self.update()

        name = self.entry_name.get()  # get the name of the conversation to analyze

        try:
            self.Program.to_html(name)
        except KeyError:  # chat wasn't found
            self.display_error("Sorry, this conversation doesn't exist")
            return

        self.label_under.config(text="Done. You can find it in the output folder!", fg="green")
