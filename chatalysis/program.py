from utility import identifyChats, getMessageFolders, checkMedia
from GUI import MainGUI


class Program:
    def __init__(self):
        self.chats = None
        self.folders = None
        self.topConversations = None
        self.topTenList = None
        self.dataDirPath = ""
        self.validDir = False
        self.gui = MainGUI(self)

    def run(self):
        self.gui.mainloop()

    def processMessagesDir(self):
        """Processes the directory with the messages for analysis"""
        self.folders = getMessageFolders(self.dataDirPath)
        self.chats = identifyChats(self.folders)
        checkMedia(self.folders)

    def dirSelected(self):
        """Checks if directory is valid (contains the 'messages' folder) and colors the entry field"""
        try:
            self.processMessagesDir()
        except Exception as e:
            self.gui.entryDataDir.config(background="#f02663")  # display directory path in red
            self.validDir = False
            self.gui.displayError(e)
            return

        self.validDir = True
        self.gui.removeLabels([self.gui.labelError])
        self.gui.entryDataDir.config(background="#17850b")  # display directory path in green
