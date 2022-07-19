import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from ctypes import windll


class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        # fix high DPI blurriness on Windows 10
        if os.name == "nt":
            windll.shcore.SetProcessDpiAwareness(1)
            self.tk.call("tk", "scaling", 1.75)

        self.title("Chatalysis")
        self.geometry("700x250")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.labelSelectDir = tk.Label(self, text="Please select directory with the messages:")
        self.labelSelectDir.grid(column=0, row=0, padx=5, pady=5)

        self.buttonSelectDir = tk.Button(
            self,
            text="Select directory",
            command=self.selectDir
        )
        self.buttonSelectDir.grid(column=0, row=1, padx=5, pady=5)

        self.dataDirPath = tk.StringVar()
        self.entryDataDir = tk.Entry(self, textvariable=self.dataDirPath, width=60)
        self.entryDataDir.grid(column=0, row=2, sticky="N", padx=5, pady=5)

        self.button1 = tk.Button(
            self,
            text="Button 1",
            command=self.selectDir
        )
        self.button1.grid(column=0, row=3, sticky="S", padx=5, pady=5)

        self.button2 = tk.Button(
            self,
            text="Button 2",
            command=self.selectDir
        )
        self.button2.grid(column=0, row=4, sticky="N", padx=5, pady=5)

        self.mainloop()

    def selectDir(self):
        dirPath = filedialog.askdirectory(title="Select source directory")
        self.dataDirPath.set(dirPath)
        self.after(20, self.dirSelected)

    def dirSelected(self):
        # if some directory was selected, display the path in green, otherwise display a red entry field
        if self.dataDirPath.get() != "":
            self.entryDataDir.config(background="#17850b")
        else:
            self.entryDataDir.config(background="#f02663")


g = GUI()
