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

        # fix high DPI blurriness on Windows 10 and add bar icon
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

        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.grid_rowconfigure(i, weight=1 if i < 3 else 0)

        self.label_select_source = ttk.Label(
            self, text="Welcome to Chatalysis!\nPlease select a message source:", justify=tk.CENTER
        )
        self.label_version = ttk.Label(self, text="", justify=tk.CENTER)

        if not is_latest_version():
            self._notify_about_latest()

        self._logo_instagram = tk.PhotoImage(file=HOME / "resources" / "images" / "instagram_small.png")
        self._logo_messenger = tk.PhotoImage(file=HOME / "resources" / "images" / "messenger_small.png")

        self.label_select_source.grid(column=1, row=0, padx=5, pady=5, columnspan=2)

        if not sys.platform == "darwin":
            # the image buttons don't match the background color even with the translucent background
            # therefore this feature is only available on Windows and Linux
            self.button_messenger = tk.Button(
                self, image=self._logo_messenger, borderwidth=0, command=lambda: self._create_main(Messenger)
            )
            self.button_instagram = tk.Button(
                self, image=self._logo_instagram, borderwidth=0, command=lambda: self._create_main(Instagram)
            )

            self.button_messenger.grid(column=0, row=1, sticky="E", columnspan=2, padx=50)
            self.button_instagram.grid(column=2, row=1, sticky="W", columnspan=2, padx=50)
        else:
            self.button_messenger = tkm.Button(
                self, text="Messenger", command=lambda: self._create_main(Messenger), height=50
            )
            self.button_instagram = tkm.Button(
                self, text="Instagram", command=lambda: self._create_main(Instagram), height=50
            )

            self.button_messenger.grid(column=0, row=1, sticky="E", columnspan=2, padx=50, ipady=10, ipadx=10)
            self.button_instagram.grid(column=2, row=1, sticky="W", columnspan=2, padx=50, ipady=10, ipadx=10)

        self._ui_elements.extend([self.label_select_source, self.button_messenger, self.button_instagram])

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
            self.progress_bar
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

        self.label_version.grid(column=1, row=3, padx=5, pady=5, columnspan=2)
        self.button_download.grid(column=1, row=4, padx=5, pady=10, columnspan=2)

        self._ui_elements.append(self.label_version)
        self._ui_elements.append(self.button_download)

    def select_dir(self, source_class: Type[MessageSource]) -> None:
        """Selects directory with the data using a dialog window and creates an instance of the message source.

        :param source_class: class of the selected message source
        """
        self.Program.data_dir_path = filedialog.askdirectory(
            title="Select source directory",
            initialdir=self.Program.config.load(source_class.__name__.lower(), "Source_dirs"),
        )
        self.data_dir_path_tk.set(self.Program.data_dir_path)

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
