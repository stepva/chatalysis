from __future__ import annotations
from typing import Any, TYPE_CHECKING
import os
import tkinter as tk

from gui.singleton_window import SingletonWindow
from gui.gui_utils import show_error
from utils.utility import creation_date

if TYPE_CHECKING:
    from gui.main_gui import MainGUI


class WindowIndividual(SingletonWindow):
    def __init__(self, program: Any, main_gui: MainGUI) -> None:
        SingletonWindow.__init__(self)
        self.Program = program
        self.main_gui = main_gui
        self.main_gui.window_individual = self

        self.title("Analyze individual conversations")
        self.geometry("600x400")

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
        self.searched_name.trace("w", self._filter_name_list)

        self.conversation_names = self._create_name_dict()

        # Entry for entering the conversation name, it's bound to start the analysis when the user hits Enter.
        # Also sets focus on name_entry for immediate writing action.
        self.name_entry = tk.Entry(self, width=56, textvariable=self.searched_name)
        self.name_entry.bind("<Return>", lambda x: self.analyze_individual())
        self.name_entry.bind("<Down>", self._listbox_select_first)
        self.name_entry.focus_set()

        string_names = " ".join(self.conversation_names.keys())
        self.name_list = tk.StringVar(self, value=string_names)

        self.name_box: tk.Listbox = tk.Listbox(self, listvariable=self.name_list, height=8, width=56)
        self.name_box.bind("<Double-1>", self._listbox_name_selected)
        self.name_box.bind("<Return>", self._listbox_name_selected)

        self.name_box_scrollbar = tk.Scrollbar(self, command=self.name_box.yview)
        self.name_box.config(yscrollcommand=self.name_box_scrollbar.set)

        self.label_instructions.grid(column=0, row=0)
        self.name_entry.grid(column=0, row=1, pady=(5, 0))
        self.name_box.grid(column=0, row=2, pady=0)
        self.name_box_scrollbar.grid(column=0, row=2, sticky="NS", padx=(490, 0), pady=(2, 0))
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

    def _listbox_select_first(self, _event: Any) -> None:
        """Selects the first item in the listbox"""
        self.name_box.focus_set()
        self.name_box.selection_anchor(0)
        self.name_box.selection_set(tk.ANCHOR)

    def analyze_individual(self, name: str = "", _event: None | tk.Event = None) -> None:
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

    def _close(self) -> None:
        self.main_gui.window_individual = None
        self.destroy()
