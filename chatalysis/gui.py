# Standard library imports
import os
import abc
import ctypes
import tkinter as tk
from tkinter import filedialog

# Application imports
from analysis import topTen
from chatalysis import htmllyse
from messenger import FacebookMessenger

# Third party imports
from tabulate import tabulate


class Window(tk.Tk):
    """Tkinter window base class"""

    def __init__(self):
        tk.Tk.__init__(self)

    @abc.abstractmethod
    def displayError(self, errorMessage: str):
        """Displays an error message in the window

        :param errorMessage: message to be displayed
        """
        pass

    @staticmethod
    def removeLabels(labels: "list[tk.Label]"):
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
        self.labelError = None
        self.Program = program
        self.create()

    def create(self):
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
        self.buttonSelectDir = tk.Button(
            self, text="Select directory", command=self.selectDir
        )
        self.button1 = tk.Button(
            self,
            text="Show top conversations",
            command=lambda: WindowTopTen(self.Program, self),
        )
        self.button2 = tk.Button(
            self,
            text="Analyze individual conversations",
            command=lambda: WindowIndividual(self.Program, self),
        )

        # Create labels
        self.labelError = tk.Label(self, text="", fg="red", wraplength=650)
        self.labelSelectDir = tk.Label(self, text="Please select directory with the messages:")

        # Create entry widgets
        self.dataDirPathTk = tk.StringVar()
        self.entryDataDir = tk.Entry(self, textvariable=self.dataDirPathTk, width=60)
        self.entryDataDir.config(background="#f02663")  # display directory path in red until a valid path is entered

        # Render objects onto a grid
        self.labelSelectDir.grid(column=0, row=0, padx=5, pady=5)
        self.buttonSelectDir.grid(column=0, row=1, padx=5, pady=5)
        self.entryDataDir.grid(column=0, row=2, sticky="N", padx=5, pady=5)
        self.button1.grid(column=0, row=3, sticky="S", padx=5, pady=5)
        self.button2.grid(column=0, row=4, sticky="N", padx=5, pady=5)
        self.labelError.grid(column=0, row=5, padx=5, pady=5)

    def displayError(self, errorMessage: str):
        self.labelError.config(text=errorMessage, fg="red")

    def selectDir(self):
        """Selects directory with the data using a dialog window"""
        self.Program.dataDirPath = filedialog.askdirectory(
            title="Select source directory", initialdir=os.getcwd()
        )
        self.dataDirPathTk.set(self.Program.dataDirPath)
        self.after(20, self.Program.dirSelected)  # check if directory is valid

        self.Program.source = FacebookMessenger(self.Program.dataDirPath)


class WindowTopTen(Window):
    """Window showing the top 10 individual conversations & top 5 group chats"""

    def __init__(self, program, gui: MainGUI):
        if not program.validDir:  # don't do anything if source directory is invalid to avoid errors
            gui.displayError("Cannot analyze until a valid directory is selected")
            return

        self.Program = program

        Window.__init__(self)
        self.title("Top conversations")
        self.geometry("600x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.labelAnalyzing = tk.Label(self, text="Analyzing...")
        self.labelError = None
        self.labelTop = None

        self.showTop()  # runs the top 10 analysis & print

    def displayError(self, errorMessage: str):
        self.removeLabels([self.labelError])

        self.labelError = tk.Label(self, text=errorMessage, wraplength=650, fg="red")
        self.labelError.grid(column=0, row=1, padx=5, pady=5)

    def showTop(self):
        """Analyzes and shows the top conversations"""
        # Calculate the top conversations if not done already
        if self.Program.topTenIndividual is None:
            self.labelAnalyzing.grid(column=0, row=0, padx=5, pady=5)
            self.update()

            topIndividual, topGroup = topTen(self.Program.dataDirPath)
            self.Program.topTenIndividual = tabulate(
                topIndividual.items(),
                headers=["Conversation", "Messages"],
                colalign=("left", "right",)
            )

            self.Program.topFiveGroups = tabulate(topGroup.items(),
                                                  headers=["Conversation", "Messages"],
                                                  colalign=("left", "right"))

        self.removeLabels([self.labelAnalyzing])  # remove the "Analyzing..." label if present

        # Print the top conversation, fixed font is necessary for the correct table formatting done by tabulate
        self.labelTop = tk.Label(
            self,
            text="\n".join(["Top 10 individual conversations\n",
                            self.Program.topTenIndividual,
                            "\n",
                            "Top 5 group chats\n",
                            self.Program.topFiveGroups]),
            anchor="n",
            font=("TkFixedFont",)
        )
        self.labelTop.grid(column=0, row=0)


class WindowIndividual(Window):
    def __init__(self, program, gui: MainGUI):
        if not program.validDir:  # don't do anything if source directory is invalid to avoid errors
            gui.displayError("Cannot analyze until a valid directory is selected")
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

        self.labelInstructions = tk.Label(
            self,
            text="Please enter conversation name in the format 'namesurname' without special characters (for example: johnsmith)",
            wraplength=450,
        )

        # add an invisible label so that the labels indicating success or error stay in the same place
        # the entire time without the rest of the objects "jumping" around
        self.labelUnder = tk.Label(self, text="", wraplength=650, fg="red")

        # Entry for entering the conversation name. It's bound to start the analysis when the user hits Enter.
        self.entryName = tk.Entry(self, width=50)
        self.entryName.bind("<Return>", self.analyzeIndividual)

        self.labelInstructions.grid(column=0, row=0, sticky="S", padx=5, pady=5)
        self.entryName.grid(column=0, row=1, sticky="N", padx=5, pady=5)
        self.labelUnder.grid(column=0, row=2, padx=5, pady=5)

    def displayError(self, errorMessage: str):
        self.labelUnder.config(text=errorMessage, fg="red")

    def analyzeIndividual(self, event: tk.Event):
        """Analyzes an individual conversation and prints information about the process

        :param event: the event bound to the key press - not used, but it doesn't work without it
        """
        self.labelUnder.config(text="Analyzing...", fg="black")
        self.update()

        # Get the name of the conversation to analyze
        name = self.entryName.get()
        chat = self.Program.source.get_chat(name)

        if chat is not None:
            # chat was found and successfully analyzed
            htmllyse(chat, self.Program.source.folders)
            self.labelUnder.config(text="Done. You can find it in the output folder!", fg="green")
        else:
            # chat wasn't found
            self.displayError("Sorry, this conversation doesn't exist")
