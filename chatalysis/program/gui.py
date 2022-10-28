import ctypes
import sys
import tkinter as tk
import tkmacosx as tkm
import traceback
from collections import OrderedDict
from tkinter import ttk, filedialog, messagebox
from typing import Type

from tabulate import tabulate

from sources.message_source import MessageSource, NoMessageFilesError
from sources.instagram import Instagram
from sources.messenger import Messenger
from utils.utility import get_file_path, open_html


def show_error(window: tk.Tk | tk.Toplevel, err_message: str):
    """Shows an error and places the last open GUI window back on top

    :param window: last open GUI window
    :param err_message: error message to display
    """
    tk.messagebox.showerror("Error", err_message)
    window.lift()


class MainGUI(tk.Tk):
    """Main GUI for the program"""

    def __init__(self, program):
        tk.Tk.__init__(self)
        self.label_under = None
        self.Program = program
        self._create_source_selection()

    def _create_source_selection(self):
        """Creates a menu for selecting the message source"""
        # fix high DPI blurriness on Windows 10
        if sys.platform == "win32" or sys.platform == "cygwin":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            self.tk.call("tk", "scaling", 1.75)

        self.title("Chatalysis")
        self.geometry("700x350")

        self.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        self.label_select_source = ttk.Label(
            self, text="Welcome to Chatalysis!\nPlease select a message source:", justify=tk.CENTER
        )
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

    def _create_main(self, source_class: Type[MessageSource]):
        """Creates the main menu
        :param source_class: class of the selected message source
        """
        # Clear source selection menu
        self.label_select_source.destroy()
        self.button_messenger.destroy()
        self.button_instagram.destroy()

        # Configure grids & columns
        self.grid_columnconfigure(0, weight=1)
        for i in range(2, 6):
            self.grid_rowconfigure(i, weight=1)

        # Create buttons
        self.button_select_dir = ttk.Button(self, text="Select folder", command=lambda: self.select_dir(source_class))
        self.button1 = ttk.Button(
            self, text="Show top conversations", command=lambda: self._try_create_window(WindowTopTen)
        )
        self.button2 = ttk.Button(
            self, text="Analyze individual conversations", command=lambda: self._try_create_window(WindowIndividual)
        )
        self.button3 = ttk.Button(
            self, text="Show your overall personal stats", command=lambda: self.show_personal(source_class)
        )

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
        self.label_under.grid(column=0, row=6, pady=5)

    def select_dir(self, source_class: Type[MessageSource]):
        """Selects directory with the data using a dialog window and creates an instance of the message source.

        :param source_class: class of the selected message source
        """
        self.Program.data_dir_path = filedialog.askdirectory(
            title="Select source directory", initialdir=self.Program.config.load(source_class.__name__, "Source_dirs")
        )
        self.data_dir_path_tk.set(self.Program.data_dir_path)

        try:
            # create message source instance filled with data from the selected dir
            self.Program.source = source_class(self.Program.data_dir_path)
        except Exception as e:
            # directory is not valid (missing 'messages' folder or other issue)
            self.entry_data_dir.config(background="#f02663")  # display directory path in red
            self.Program.valid_dir = False

            if self.Program.config.load("print_stacktrace", "dev", is_bool=True):
                show_error(self, f"{repr(e)}\n\n{traceback.format_exc()}")
            else:
                show_error(self, repr(e))
            return

        self.Program.config.save(source_class.__name__, self.Program.data_dir_path, "Source_dirs")  # save last used dir
        self.Program.valid_dir = True
        self.label_under.config(text="")
        self.entry_data_dir.config(background="#17850b")  # display directory path in green

    def show_personal(self, source_class: Type[MessageSource]):
        """Opens (and creates if necessary) personal stats.

        :param source_class: class of the selected message source
        """
        if not self.Program.valid_dir:
            # don't do anything if source directory is invalid to avoid errors
            show_error(self, "Cannot analyze until a valid directory is selected")
            return

        if not self.Program.personal_stats:
            self.label_under.config(text="Analyzing... (this may take a while)", fg="black")
            self.update()
            self.Program.personal_to_html()
        else:
            open_html(get_file_path("Personal stats", source_class.__name__))

        self.label_under.config(text="Done. You can find it in the output folder!", fg="green")

    def _try_create_window(self, window_class: Type[tk.Toplevel]):
        if self.Program.valid_dir:
            window_class(self.Program)
        else:
            show_error(self, "Cannot analyze until a valid directory is selected")


class WindowTopTen(tk.Toplevel):
    """Window showing the top 10 individual conversations & top 5 group chats"""

    def __init__(self, program):
        tk.Toplevel.__init__(self)
        self.Program = program

        self.title("Top conversations")
        self.geometry("600x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label_analyzing = tk.Label(self, text="Analyzing...")
        self.label_error = None
        self.label_top = None

        self.show_top()  # runs the top 10 analysis & print

    def show_top(self):
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
    def __init__(self, program):
        tk.Toplevel.__init__(self)
        self.Program = program

        self.title("Analyze individual conversations")
        self.geometry("600x400")
        self._create()

    def _create(self):
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
        self.searched_name.trace("w", self._filter_name_list)

        original_names = [(chat_id.split("_")[0].lower(), chat_id) for chat_id in sorted(self.Program.source.chat_ids)]
        self.conversation_names = self._create_name_dict(original_names)

        # Entry for entering the conversation name, it's bound to start the analysis when the user hits Enter.
        # Also sets focus on name_entry for immediate writing action.
        self.name_entry = tk.Entry(self, width=56, textvariable=self.searched_name)
        self.name_entry.bind("<Return>", lambda x: self.analyze_individual())
        self.name_entry.bind("<Down>", lambda x: self.name_box.focus_set())
        self.name_entry.focus_set()

        string_names = " ".join(self.conversation_names.keys())
        self.name_list = tk.StringVar(self, value=string_names)

        self.name_box = tk.Listbox(self, listvariable=self.name_list, height=8, width=56)
        self.name_box.bind("<Double-1>", self._listbox_name_selected)
        self.name_box.bind("<Return>", self._listbox_name_selected)

        self.label_instructions.grid(column=0, row=0)
        self.name_entry.grid(column=0, row=1, pady=(5, 0))
        self.name_box.grid(column=0, row=2, pady=(0, 5))
        self.label_under.grid(column=0, row=3, pady=5)

    def _create_name_dict(self, original_names: list[tuple]) -> dict:
        """Creates a dict with names of conversations and their chat IDs. If two conversations have the same name,
        the number of messages is added to the conversation name, to distinguish between them.

        :param original_names: list of all available conversations, stored as tuples (name, chat_id)
        :return: dict with conversation names
        """
        conversations: OrderedDict[str, str] = OrderedDict()

        for name, chat_id in original_names:
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

        return conversations

    def _filter_name_list(self, *_args):
        """Updates the listbox to show names starting with the searched string"""
        self.label_under.config(text="")
        new_names = []

        for n in self.conversation_names.keys():
            if n.startswith(self.searched_name.get()):
                new_names.append(n)

        string_new_names = " ".join(new_names)
        self.name_list.set(string_new_names)

    def _listbox_name_selected(self, *_args):
        """Takes the selected name from the listbox and runs the analysis"""
        current_selection = self.name_box.curselection()
        selected_name = self.conversation_names[self.name_box.get(current_selection)]
        self.analyze_individual(selected_name)

    def analyze_individual(self, name: str = "", _event: tk.Event = None):
        """Analyzes an individual conversation and prints information about the process

        :param name: name of the conversation to analyze
        :param _event: tkinter event
        """
        self.label_under.config(text="Analyzing...", fg="black")
        self.update()

        try:
            if not name:
                name = self.conversation_names[self.name_entry.get()]
            self.Program.chat_to_html(name)
        except KeyError:  # chat wasn't found
            show_error(self, f"Sorry, conversation {self.name_entry.get()} doesn't exist")
            return
        except NoMessageFilesError as e:
            if self.Program.config.load("print_stacktrace", "dev", is_bool=True):
                show_error(self, f"{repr(e)}\n\n{traceback.format_exc()}")
            else:
                show_error(self, repr(e))
            return

        self.label_under.config(text="Done. You can find it in the output folder!", fg="green")
