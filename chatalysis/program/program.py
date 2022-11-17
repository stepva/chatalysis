import io
import os
from pprint import pprint
from typing import Any

from __init__ import __version__
from chats.analyzer import Analyzer
from chats.stats import Stats
from GUI.main_gui import MainGUI
from sources.messenger import Messenger
from utils.utility import get_file_path, open_html
from utils.config import Config


class Program:
    def __init__(self) -> None:
        self.source: Any = None
        self.gui: Any = None

        self.config = Config()
        self.print_stacktrace = self.config.load("print_stacktrace", "dev", is_bool=True)

        self.top_ten_individual: Any = None
        self.top_five_groups: Any = None
        self.personal_stats: Any = None

        self.data_dir_path = ""
        self.valid_dir = False

    def reset_stored_data(self) -> None:
        """Resets cached data from a particualr message source"""
        self.top_ten_individual = None
        self.top_five_groups = None
        self.personal_stats = None

    def run(self, cli: bool = False) -> None:
        if cli:
            self.cli()
        else:
            self.gui = MainGUI(self)
            self.gui.mainloop()

    def chat_to_html(self, name: str) -> Any:
        chat = self.source.get_chat(name)
        self.to_html(chat)

    def to_html(self, chat: Stats) -> None:
        """Analyzes any type of chat (or PersonalStats), creates an HTML output file and opens it in the browser.

        :param chat: Chat or PersonalStats to analyze
        """
        file_path = get_file_path(chat.title, self.source.__class__.__name__)

        analyzer = Analyzer(chat)
        source = analyzer.create_html()

        with io.open(file_path, "w", encoding="utf-8") as data:
            data.write(source)

        open_html(file_path)

    def to_cli(self, chat_name: str) -> None:
        """Analyzes the chat and prints the stats to terminal"""
        chat = self.source.get_chat(chat_name)
        analyzer = Analyzer(chat)

        print(f"Chat: {chat.title}, from {chat.from_day} to {chat.to_day}")
        pprint(analyzer.chat_stats(chat.participants), indent=2, sort_dicts=True)
        pprint(analyzer.reaction_stats(chat.reactions, chat.names, chat.people), indent=2, sort_dicts=False)
        pprint(analyzer.emoji_stats(chat.emojis, chat.names, chat.people), indent=2, sort_dicts=False)
        pprint(analyzer.time_stats(chat.times), indent=2, sort_dicts=False)
        pprint(chat.first_message(), indent=2, sort_dicts=False)

    def cli(self) -> None:
        """CLI loop used mainly for testing purposes"""
        self.data_dir_path = os.getcwd()
        try:
            self.source = Messenger(self.data_dir_path)
        except Exception as e:
            print(f"Not a valid source - {e}")
            return
        folders = self.source.folders
        chats = self.source.chat_ids
        if not folders:
            print(
                'Looks like there is no messages folder here. Make sure to add the "messages" folder downloaded from Facebook to the chatalysis parent folder. More info in the README :)'
            )
            exit()

        tops = None
        i = ""

        print("************************************")
        print(f"Welcome to Chatalysis {__version__}!\n")
        print(
            """To see your Top 10 chats, just type \"top\"
    To chatalyse a specific conversation, just say which one - \"namesurname\"
    If you need help, read the README
    To exit, just type \"exit\":
            """
        )

        while i != "exit":
            print("What do you want to do?")
            i = input()
            chat = chats.get(i)

            if i == "top":
                print("\nLoading...\n")
                if not tops:
                    tops = self.source.top_ten()

                pprint(tops, indent=2, sort_dicts=False)

            elif chat is not None:
                print("\nLoading...\n")
                self.to_html(i)
                self.to_cli(i)
                print("Done. You can find it in the output folder!\n")

            elif i != "exit":
                print(f"No chats named {i}. Try again.")

        return
