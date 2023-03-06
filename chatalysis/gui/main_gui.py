import ctypes
import sys
import tkinter as tk
import tkmacosx as tkm
from tkinter import ttk, filedialog
from typing import Any, Optional, Type

from paths import HOME
from sources.message_source import MessageSource
from sources.instagram import Instagram
from sources.messenger import Messenger
from sources.whatsapp import WhatsApp
from utils.utility import is_latest_version, download_latest
from gui.window_top_ten import WindowTopTen
from gui.window_individual import WindowIndividual
from gui.gui_utils import show_error


class MainGUI(tk.Tk):
    """Main GUI for the program"""

    def __init__(self, program: Any) -> None:
        tk.Tk.__init__(self)
        self.label_under: Any = None
        self.Program = program

        # fix high DPI blurriness on Windows 10
        if sys.platform == "win32" or sys.platform == "cygwin":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            self.tk.call("tk", "scaling", 1.75)

        self.iconbitmap(HOME / "resources" / "images" / "icon.ico")
        self.geometry("700x350")
        self.resizable(False, False)  # disable maximize button

        self.window_top_ten: Optional[WindowTopTen] = None
        self.window_individual: Optional[WindowIndividual] = None

        self._ui_elements: list[tk.BaseWidget] = []
        self._create_source_selection()

    def _create_source_selection(self) -> None:
        """Creates a menu for selecting the message source"""
        self.title("Chatalysis")
        for el in self._ui_elements:  # clear previous widgets
            el.destroy()

        self._source_selection_rows = 4

        self.grid_columnconfigure(0, weight=1)
        for i in range(self._source_selection_rows + 2):
            self.grid_rowconfigure(i, weight=1)

        self.label_select_source = ttk.Label(
            self, text="Welcome to Chatalysis!\nPlease select a message source:", justify=tk.CENTER
        )
        self.label_version = ttk.Label(self, text="", justify=tk.CENTER)

        if not is_latest_version():
            self._notify_about_latest()

        if sys.platform == "darwin":
            self.button_messenger = tkm.Button(
                self, text="Facebook Messenger", command=lambda: self._create_main(Messenger), height=50
            )
            self.button_instagram = tkm.Button(
                self, text="Instagram", command=lambda: self._create_main(Instagram), height=50
            )
            self.button_whatsapp = tkm.Button(
                self, text="WhatsApp", command=lambda: self._create_whatsapp_menu(), height=50
            )
        else:
            self.button_messenger = ttk.Button(
                self, text="Facebook Messenger", command=lambda: self._create_main(Messenger)
            )
            self.button_instagram = ttk.Button(self, text="Instagram", command=lambda: self._create_main(Instagram))
            self.button_whatsapp = ttk.Button(self, text="WhatsApp", command=lambda: self._create_whatsapp_menu())

        self.label_select_source.grid(column=0, row=0, padx=5, pady=5)
        self.button_messenger.grid(column=0, row=1, ipady=10, ipadx=10)
        self.button_instagram.grid(column=0, row=2, ipady=10, ipadx=10)
        self.button_whatsapp.grid(column=0, row=3, ipady=10, ipadx=10)

        self._ui_elements.extend(
            [self.label_select_source, self.button_messenger, self.button_instagram, self.button_whatsapp]
        )

    def _create_main(self, source_class: Type[MessageSource]) -> None:
        """Creates the main menu
        :param source_class: class of the selected message source
        """
        self.title(f"Chatalysis - {source_class.__name__}")

        self.Program.valid_dir = False
        for el in self._ui_elements:  # clear source selection menu
            el.destroy()

        # Configure grids & columns
        self.grid_columnconfigure(0, weight=1)
        for i in range(2, 7):
            self.grid_rowconfigure(i, weight=1)

        # Create buttons
        self.button_select_dir = ttk.Button(self, text="Select folder", command=lambda: self.select_dir(source_class))
        self.button1 = ttk.Button(
            self, text="Show top conversations", command=lambda: self._try_create_window("top_ten")
        )
        self.button2 = ttk.Button(
            self, text="Analyze individual conversations", command=lambda: self._try_create_window("individual")
        )
        self.button3 = ttk.Button(self, text="Show your overall personal stats", command=self.show_personal)
        self.button_back = ttk.Button(self, text="Back", command=lambda: self._create_source_selection())

        # Create labels
        self.label_under = tk.Label(self, text="", wraplength=650)
        self.label_select_dir = ttk.Label(self, text="Please select folder with the messages:")

        # Create entry widgets
        self.data_dir_path_tk = tk.StringVar()
        self.entry_data_dir = tk.Entry(self, textvariable=self.data_dir_path_tk, width=60)
        self.entry_data_dir.config(background="#f02663")  # display directory path in red until a valid path is entered

        # Create progress bar
        self.progress_bar = ttk.Progressbar(self, length=300, mode="determinate")

        # Render objects onto a grid
        self.label_select_dir.grid(column=0, row=0, pady=5)
        self.button_select_dir.grid(column=0, row=1)
        self.entry_data_dir.grid(column=0, row=2)
        self.button1.grid(column=0, row=3, sticky="S")
        self.button2.grid(column=0, row=4)
        self.button3.grid(column=0, row=5, sticky="N")
        self.button_back.grid(column=0, row=6, padx=(610, 15))
        self.label_under.grid(column=0, row=6, pady=5)

        self._ui_elements = [
            self.label_select_dir,
            self.button_select_dir,
            self.entry_data_dir,
            self.button1,
            self.button2,
            self.button3,
            self.button_back,
            self.label_under,
            self.progress_bar,
        ]

    def _create_whatsapp_menu(self, source_class: Type[MessageSource] = WhatsApp) -> None:
        """Creates the menu for WhatsApp"""
        self.title("Chatalysis - WhatsApp")

        self.Program.valid_dir = False
        for el in self._ui_elements:  # clear source selection menu
            el.destroy()

        # Configure grids & columns
        self.grid_columnconfigure(0, weight=1)
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)

        # Create buttons
        self.button_select_dir = ttk.Button(self, text="Select file", command=lambda: self.select_file(source_class))
        self.button_back = ttk.Button(self, text="Back", command=lambda: self._create_source_selection())

        # Create labels
        self.label_under = tk.Label(self, text="", wraplength=650)
        self.label_select_dir = ttk.Label(self, text="Please select a file with the messages:")

        # Create entry widgets
        self.data_dir_path_tk = tk.StringVar()
        self.entry_data_dir = tk.Entry(self, textvariable=self.data_dir_path_tk, width=60)
        self.entry_data_dir.config(background="#f02663")  # display directory path in red until a valid path is entered

        # Render objects onto a grid
        self.label_select_dir.grid(column=0, row=1, sticky="S", pady=5)
        self.button_select_dir.grid(column=0, row=2)
        self.entry_data_dir.grid(column=0, row=3, sticky="N")
        self.button_back.grid(column=0, row=6, padx=(610, 15))
        self.label_under.grid(column=0, row=6, pady=5)

        self._ui_elements = [
            self.label_select_dir,
            self.button_select_dir,
            self.entry_data_dir,
            self.button_back,
            self.label_under,
        ]

    def _notify_about_latest(self) -> None:
        """Creates a label notifying about a newer version of Chatalysis and button which downloads t."""
        self.label_version = ttk.Label(
            self,
            text="Looks like you don't have the latest version of Chatalysis.\n"
            "We recommend that you download it to get all the new features.",
            justify=tk.CENTER,
        )
        self.button_download = ttk.Button(self, text="Download", command=download_latest)

        self.label_version.grid(column=0, row=self._source_selection_rows, padx=5, pady=5)
        self.button_download.grid(column=0, row=self._source_selection_rows + 1, padx=5, pady=(5, 10))

        self._ui_elements.append(self.label_version)
        self._ui_elements.append(self.button_download)

    def select_file(self, source_class: Type[MessageSource]) -> None:
        """Selects a file with data using a dialog window. It is assumed that the file contains only a single chat,
        which is immediately exported to HTML. Currently used only for WhatsApp.

        :param source_class: class of the selected message source
        """
        self.Program.data_dir_path = filedialog.askopenfilename(
            filetypes=[("Text file", ".txt")],
            title="Select source file",
            initialdir=self.Program.config.load(source_class.__name__.lower(), "Source_dirs"),
        )
        self.data_dir_path_tk.set(self.Program.data_dir_path)
        self._instantiate_message_source(source_class)

        self.label_under.config(text="Analyzing...", fg="black")
        self.update()

        try:
            self.Program.chat_to_html("dummy")
        except Exception as e:
            show_error(self, repr(e), self.Program.print_stacktrace)
            self.label_under.config(text="")
            return

        self.label_under.config(text="Done. You can find it in the output folder!", fg="green")

    def select_dir(self, source_class: Type[MessageSource]) -> None:
        """Selects a directory with data using a dialog window.

        :param source_class: class of the selected message source
        """
        self.Program.data_dir_path = filedialog.askdirectory(
            title="Select source directory",
            initialdir=self.Program.config.load(source_class.__name__.lower(), "Source_dirs"),
        )
        self.data_dir_path_tk.set(self.Program.data_dir_path)
        self._instantiate_message_source(source_class)

    def _instantiate_message_source(self, source_class: Type[MessageSource]) -> None:
        """Creates an instance of the message source after the data path is selected.

        :param source_class: class of the selected message source
        """
        try:
            # create message source instance filled with data from the selected dir
            self.Program.source = source_class(self.Program.data_dir_path)
        except Exception as e:
            # directory is not valid (missing 'messages' folder or other issue)
            self.entry_data_dir.config(background="#f02663")  # display directory path in red
            self.Program.valid_dir = False
            show_error(self, repr(e), self.Program.print_stacktrace)
            return

        # save last used dir
        self.Program.config.save(source_class.__name__.lower(), self.Program.data_dir_path, "Source_dirs")
        self.Program.valid_dir = True

        self.label_under.config(text="")
        self.entry_data_dir.config(background="#17850b")  # display directory path in green

    def show_personal(self) -> None:
        """Opens (and creates if necessary) personal stats."""
        if not self.Program.valid_dir:
            # don't do anything if source directory is invalid to avoid errors
            show_error(self, "Cannot analyze until a valid directory is selected", False)
            return

        self.progress_bar.grid(column=0, row=6, pady=5)

        try:
            self.Program.personal_stats = self.Program.source.personal_stats(self)

            self.progress_bar.destroy()
            self.label_under.config(text="Done. You can find it in the output folder!", fg="green")
            self.update()

            self.Program.to_html(self.Program.personal_stats)

        except Exception as e:
            show_error(self, repr(e), self.Program.print_stacktrace)
            return

    def _try_create_window(self, window_type: str) -> None:
        if self.Program.valid_dir:
            if window_type == "top_ten":
                WindowTopTen(self.Program, self) if not self.window_top_ten else self.window_top_ten.lift()
            elif window_type == "individual":
                WindowIndividual(self.Program, self) if not self.window_individual else self.window_individual.lift()
        else:
            show_error(self, "Cannot analyze until a valid directory is selected", False)
