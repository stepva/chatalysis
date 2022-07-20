import os
import time
import tkinter as tk
from tkinter import filedialog
from ctypes import windll
from pprint import pformat
from utility import identifyChats, getMessageFolders, checkMedia
from analysis import topTen
from chatalysis import htmllyse


class Program:
    """The program and its GUI. Needs refactor, but it works for now"""

    def __init__(self):
        self.chats = None
        self.folders = None
        self.topConversations = None
        self.dataDirPath = ""
        self.validDir = False

        self.gui = tk.Tk()
        self.createMainGUI()
    
    def run(self):
        self.gui.mainloop()

    def processMessagesDir(self):
        """Processes the directory with the messages for analysis"""
        self.folders = getMessageFolders(self.dataDirPath)
        self.chats = identifyChats(self.folders)
        checkMedia(self.folders)

    def createMainGUI(self):
        """Creates the main GUI window"""

        # fix high DPI blurriness on Windows 10
        if os.name == "nt":
            windll.shcore.SetProcessDpiAwareness(1)
            self.gui.tk.call("tk", "scaling", 1.75)

        self.gui.title("Chatalysis")
        self.gui.geometry("800x300")

        # Configure grids & columns
        self.gui.grid_columnconfigure(0, weight=1)
        for i in range(2, 5):
            self.gui.grid_rowconfigure(i, weight=1)

        # Create buttons
        self.gui.buttonSelectDir = tk.Button(
            self.gui,
            text="Select directory",
            command=self.selectDir
        )
        self.gui.button1 = tk.Button(
            self.gui,
            text="Show top 10 (individual) conversations",
            command=self.showTopTen
        )
        self.gui.button2 = tk.Button(
            self.gui,
            text="Analyze individual conversations",
            command=self.createWindowIndividual
        )

        # Create labels
        self.gui.labelSelectDir = tk.Label(self.gui, text="Please select directory with the messages:")

        # Create entry widgets
        self.gui.dataDirPathTk = tk.StringVar()
        self.gui.entryDataDir = tk.Entry(self.gui, textvariable=self.gui.dataDirPathTk, width=60)
        self.gui.entryDataDir.config(background="#f02663")  # display directory path in red until a valid path is entered

        # Render objects onto a grid
        self.gui.labelSelectDir.grid(column=0, row=0, padx=5, pady=5)
        self.gui.buttonSelectDir.grid(column=0, row=1, padx=5, pady=5)
        self.gui.entryDataDir.grid(column=0, row=2, sticky="N", padx=5, pady=5)
        self.gui.button1.grid(column=0, row=3, sticky="S", padx=5, pady=5)
        self.gui.button2.grid(column=0, row=4, sticky="N", padx=5, pady=5)

        self.gui.errorMessage = None

    def createWindowTopTen(self):
        """Creates a separate window for the top 10 conversations"""
        self.windowTopTen = tk.Tk()
        self.windowTopTen.title("Top 10 conversations")
        self.windowTopTen.geometry("420x300")

        self.windowTopTen.grid_columnconfigure(0, weight=1)
        self.windowTopTen.grid_rowconfigure(0, weight=1)

        self.windowTopTen.labelAnalyzing = tk.Label(self.windowTopTen, text="Analyzing...")

    def createWindowIndividual(self):
        """Creates a separate window for analyzing individual conversations"""
        if not self.validDir:  # don't do anything if source directory is invalid to avoid errors
            self.displayError("Cannot analyze until a valid directory is selected")
            return

        self.windowIndividual = tk.Tk()
        self.windowIndividual.title("Analyze individual conversations")
        self.windowIndividual.geometry("600x200")

        self.windowIndividual.grid_columnconfigure(0, weight=1)
        self.windowIndividual.grid_rowconfigure(0, weight=1)
        self.windowIndividual.grid_rowconfigure(1, weight=1)

        self.windowIndividual.labelInstructions = tk.Label(
            self.windowIndividual,
            text="Please enter conversation name in the format 'namesurname' without special characters (for example: johnsmith)",
            wraplength=450
        )

        self.windowIndividual.labelDone = None
        self.windowIndividual.labelFail = None

        # Entry for entering the conversation name. It's bound to start the analysis when the user hits Enter.
        self.windowIndividual.entryName = tk.Entry(self.windowIndividual, width=50)
        self.windowIndividual.entryName.bind("<Return>", self.analyzeIndividual)

        self.windowIndividual.labelInstructions.grid(column=0, row=0, sticky="S", padx=5, pady=5)
        self.windowIndividual.entryName.grid(column=0, row=1, sticky="N", padx=5, pady=5)

    def selectDir(self):
        """Selects the directory using a dialog window"""
        self.dataDirPath = filedialog.askdirectory(title="Select source directory")
        self.gui.dataDirPathTk.set(self.dataDirPath)
        self.gui.after(5, self.dirSelected)  # check if dir is valid

    def dirSelected(self):
        """Checks if directory is valid (contains the 'messages' folder) and colors the entry field"""
        try:
            self.processMessagesDir()
        except Exception as e:
            self.gui.entryDataDir.config(background="#f02663")  # display directory path in red
            self.validDir = False
            self.displayError(e)
            return

        self.validDir = True
        self.removeLabels([self.gui.errorMessage])
        self.gui.entryDataDir.config(background="#17850b")  # display directory path in green

    def displayError(self, errorString: str):
        """Displays an error message on the main GUI"""
        self.removeLabels([self.gui.errorMessage])

        self.gui.errorMessage = tk.Label(self.gui, text=errorString, wraplength=650, fg="red")
        self.gui.errorMessage.grid(column=0, row=5, padx=5, pady=5)

    def showTopTen(self):
        """Shows the top 10 conversations in a separate window"""
        if not self.validDir:  # don't do anything if source directory is invalid to avoid errors
            self.displayError("Cannot analyze until a valid directory is selected")
            return

        self.createWindowTopTen()

        # Calculate the top 10 conversations if not done already
        if self.topConversations is None:
            self.windowTopTen.labelAnalyzing.grid(column=0, row=0, padx=5, pady=5)
            self.windowTopTen.update()

            self.topConversations = topTen(self.dataDirPath)

        topTenList = pformat(self.topConversations, indent=2, sort_dicts=False)

        self.removeLabels([self.windowTopTen.labelAnalyzing])  # remove the "Analyzing..." label if present

        self.windowTopTen.labelTopTen = tk.Label(self.windowTopTen, text=topTenList)  # print the top 10
        self.windowTopTen.labelTopTen.grid(column=0, row=0, padx=5, pady=5)

    def removeLabels(self, labels: list[tk.Label]):
        """Removes labels from a given window

        :param labels: list of labels to remove
        """
        for label in labels:
            if label is not None:
                label.destroy()

    def analyzeIndividual(self, event: tk.Event):
        """Analyzes an individual conversation and prints information about the process

        :param event: the event bound to the key press - not used, but it stops working if you remove it
        """
        self.removeLabels([self.windowIndividual.labelDone, self.windowIndividual.labelFail])
        self.windowIndividual.update()

        self.windowIndividual.labelAnalyzing = tk.Label(self.windowIndividual, text="Analyzing...")
        self.windowIndividual.labelAnalyzing.grid(column=0, row=2, padx=5, pady=5)

        # Get the name of the conversation to analyze
        name = self.windowIndividual.entryName.get()
        chat = self.chats.get(name)

        self.windowIndividual.labelAnalyzing.destroy()  # remove the "Analyzing..." label

        if chat is not None:
            # chat was found and successfully analyzed
            htmllyse(chat, self.folders)
            self.windowIndividual.labelDone = tk.Label(self.windowIndividual,
                                                       text="Done. You can find it in the output folder!", fg="green")
            self.windowIndividual.labelDone.grid(column=0, row=2, padx=5, pady=5)
        else:
            # chat wasn't found
            self.windowIndividual.labelFail = tk.Label(self.windowIndividual,
                                                       text="Sorry, this conversation doesn't exist", fg="red")
            self.windowIndividual.labelFail.grid(column=0, row=2, padx=5, pady=5)
