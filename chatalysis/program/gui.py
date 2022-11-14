import ctypes
import sys
import os
import tkinter as tk
import tkmacosx as tkm
import traceback
from tkinter import ttk, filedialog, messagebox
from typing import Any, Type

from tabulate import tabulate

from sources.message_source import MessageSource
from sources.instagram import Instagram
from sources.messenger import Messenger
from utils.utility import is_latest_version, download_latest, creation_date


def show_error(window: tk.Tk | tk.Toplevel, err_message: str, print_stacktrace: bool) -> None:
    """Shows an error and places the last open GUI window back on top

    :param window: last open GUI window
    :param err_message: error message to display
    :param print_stacktrace: bool whether to print stacktrace of the error or not
    """
    if print_stacktrace:
        messagebox.showerror("Error", f"{err_message}\n\n{traceback.format_exc()}")
    else:
        messagebox.showerror("Error", err_message)
    window.lift()


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

        self.geometry("700x350")
        self.resizable(False, False)  # disable maximize button

        self._ui_elements: list[tk.BaseWidget] = []
        self._create_source_selection()

    def _create_source_selection(self) -> None:
        """Creates a menu for selecting the message source"""
        self.title("Chatalysis")
        for el in self._ui_elements:  # clear previous widgets
            el.destroy()

        self.grid_columnconfigure(0, weight=1)
        for i in range(7):
            self.grid_rowconfigure(i, weight=1 if i < 3 else 0)

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
        else:
            self.button_messenger = ttk.Button(
                self, text="Facebook Messenger", command=lambda: self._create_main(Messenger)
            )
            self.button_instagram = ttk.Button(self, text="Instagram", command=lambda: self._create_main(Instagram))

        self.label_select_source.grid(column=0, row=0, padx=5, pady=5)
        self.button_messenger.grid(
            column=0, row=1, sticky="S", padx=5, pady=5, ipady=0 if sys.platform == "darwin" else 10, ipadx=10
        )
        self.button_instagram.grid(
            column=0, row=2, sticky="N", padx=5, pady=(5, 50), ipady=0 if sys.platform == "darwin" else 10, ipadx=10
        )

        self._ui_elements.extend([self.label_select_source, self.button_messenger, self.button_instagram])

    def _create_main(self, source_class: Type[MessageSource]) -> None:
        """Creates the main menu
        :param source_class: class of the selected message source
        """
        self.title(f"Chatalysis - {source_class.__name__}")

        self.Program.reset_stored_data()
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
            self, text="Show top conversations", command=lambda: self._try_create_window(WindowTopTen)
        )
        self.button2 = ttk.Button(
            self, text="Analyze individual conversations", command=lambda: self._try_create_window(WindowIndividual)
        )
        self.button3 = ttk.Button(self, text="Show your overall personal stats", command=self.show_personal)
        self.button_back = ttk.Button(self, text="Back", command=lambda: self._create_source_selection())

        # Create labels
        self.label_under = tk.Label(self, text="", wraplength=650)
        self.label_select_dir = tk.Label(self, text="Please select folder with the messages:")

        # Create entry widgets
        self.data_dir_path_tk = tk.StringVar()
        self.entry_data_dir = tk.Entry(self, textvariable=self.data_dir_path_tk, width=60)
        self.entry_data_dir.config(background="#f02663")  # display directory path in red until a valid path is entered

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

        self.label_version.grid(column=0, row=3, padx=5, pady=5)
        self.button_download.grid(column=0, row=4, padx=5, pady=10)

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
        self.Program.reset_stored_data()

        self.label_under.config(text="")
        self.entry_data_dir.config(background="#17850b")  # display directory path in green

    def show_personal(self) -> None:
        """Opens (and creates if necessary) personal stats."""
        if not self.Program.valid_dir:
            # don't do anything if source directory is invalid to avoid errors
            show_error(self, "Cannot analyze until a valid directory is selected", False)
            return

        if not self.Program.personal_stats:
            self.label_under.config(text="Analyzing... (this may take a while)", fg="black")
            self.update()

            try:
                self.Program.personal_stats = self.Program.source.personal_stats()
                self.Program.to_html(self.Program.personal_stats)
            except Exception as e:
                show_error(self, repr(e), self.Program.print_stacktrace)
                return
        else:
            self.Program.to_html(self.Program.personal_stats)

        self.label_under.config(text="Done. You can find it in the output folder!", fg="green")

    def _try_create_window(self, window_class: Type[tk.Toplevel]) -> None:
        if self.Program.valid_dir:
            window_class(self.Program)
        else:
            show_error(self, "Cannot analyze until a valid directory is selected", False)


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


class WindowIndividual(tk.Toplevel):
    def __init__(self, program: Any) -> None:
        tk.Toplevel.__init__(self)
        self.Program = program

        self.title("Analyze individual conversations")
        self.geometry("600x400")
        self.resizable(False, False)
        self._create()

    def _create(self) -> None:
        """Creates and renders the objects in the window"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.label_instructions = tk.Label(
            self,
            text="Please enter conversation name in the format 'namesurname'\n"
            "without special characters (for example: johnsmith)",
            justify="center",
        )

        self.label_under = tk.Label(self, text="", wraplength=650, fg="red", justify="center")

        # set searched_name var to trace any writing action
        self.searched_name = tk.StringVar(self)
        self.searched_name.trace("w", self._filter_name_list)  # type: ignore

        self.conversation_names = self._create_name_dict()

        # Entry for entering the conversation name, it's bound to start the analysis when the user hits Enter.
        # Also sets focus on name_entry for immediate writing action.
        self.name_entry = tk.Entry(self, width=56, textvariable=self.searched_name)
        self.name_entry.bind("<Return>", lambda x: self.analyze_individual())
        self.name_entry.bind("<Down>", lambda x: self.name_box.focus_set())
        self.name_entry.focus_set()

        string_names = " ".join(self.conversation_names.keys())
        self.name_list = tk.StringVar(self, value=string_names)

        self.name_box: tk.Listbox = tk.Listbox(self, listvariable=self.name_list, height=8, width=56)
        self.name_box.bind("<Double-1>", self._listbox_name_selected)
        self.name_box.bind("<Return>", self._listbox_name_selected)

        self.label_instructions.grid(column=0, row=0)
        self.name_entry.grid(column=0, row=1, pady=(5, 0))
        self.name_box.grid(column=0, row=2, pady=(0, 5))
        self.label_under.grid(column=0, row=3, pady=5)

    def _create_name_dict(self) -> dict[str, str]:
        """Creates a dict with names of conversations and their chat IDs. If two conversations have the same name,
        the number of messages is added to the conversation name, to distinguish between them.

        :return: dict with conversation names
        """
        conversations: dict[str, str] = {}

        for chat_id, chat_paths in self.Program.source.chat_ids.items():
            # get the latest "name" of the conversation
            if len(chat_paths) > 1:
                creation_dates = [creation_date(k) for k in chat_paths]
                idx = max(range(len(creation_dates)), key=creation_dates.__getitem__)
                name = os.path.split(chat_paths[idx])[-1].split("_")[0]
            else:
                name = os.path.split(chat_paths[0])[-1].split("_")[0]

            if name in conversations:
                src = self.Program.source
                chat_id_2 = str(conversations.get(name))

                # the listbox splits entries by spaces, therefore a no-break space has to be used here
                new_name_1 = f"{name}\u00a0({src.conversation_size(chat_id)}\u00a0messages)"
                new_name_2 = f"{name}\u00a0({src.conversation_size(chat_id_2)}\u00a0messages)"

                conversations.pop(name)
                conversations[new_name_1] = chat_id
                conversations[new_name_2] = chat_id_2
            else:
                conversations[name] = chat_id

        return dict(sorted(conversations.items()))

    def _filter_name_list(self, *_args: Any) -> None:
        """Updates the listbox to show names starting with the searched string"""
        self.label_under.config(text="")
        new_names = []

        for n in self.conversation_names.keys():
            if n.startswith(self.searched_name.get()):
                new_names.append(n)

        string_new_names = " ".join(new_names)
        self.name_list.set(string_new_names)

    def _listbox_name_selected(self, *_args: Any) -> None:
        """Takes the selected name from the listbox and runs the analysis"""
        current_selection = self.name_box.curselection()  # type: ignore
        selected_name = self.conversation_names[self.name_box.get(current_selection)]
        self.analyze_individual(selected_name)

    def analyze_individual(self, name: str = "", _event: None | tk.Event = None) -> None:  # type: ignore
        """Analyzes an individual conversation and prints information about the process

        :param name: name of the conversation to analyze
        :param _event: tkinter event
        """
        self.label_under.config(text="Analyzing...", fg="black")
        self.update()

        if not name:
            if self.name_entry.get() in self.conversation_names:
                name = self.conversation_names[self.name_entry.get()]
            else:
                show_error(self, f"Sorry, conversation {self.name_entry.get()} doesn't exist", False)
                self.label_under.config(text="")
                return

        try:
            self.Program.chat_to_html(name)
        except Exception as e:
            show_error(self, repr(e), self.Program.print_stacktrace)
            self.label_under.config(text="")
            return

        self.label_under.config(text="Done. You can find it in the output folder!", fg="green")
