from gui import MainGUI


class Program:
    def __init__(self):
        self.source = None
        self.topTenIndividual = None
        self.topFiveGroups = None
        self.dataDirPath = ""
        self.validDir = False
        self.gui = MainGUI(self)

    def run(self):
        self.gui.mainloop()

    def dirSelected(self):
        """Checks if directory is valid (contains the 'messages' folder) and colors the entry field"""
        try:
            self.validDir = True
            self.gui.labelError.config(text="")
            self.gui.entryDataDir.config(
                background="#17850b"
            )  # display directory path in green
        except Exception as e:
            self.gui.entryDataDir.config(
                background="#f02663"
            )  # display directory path in red
            self.validDir = False
            self.gui.displayError(e)
            return
