# Standard library imports
import io
import os

# Third party imports
from pprint import pprint

# Application imports
from program.gui import MainGUI
from chats.analyzer import Analyzer
from utils.utility import open_html, get_file_path, check_if_create_new
from sources.messenger import FacebookMessenger
from __init__ import __version__


class Program:
    def __init__(self):
        self.source = None
        self.top_ten_individual = None
        self.top_five_groups = None
        self.data_dir_path = ""
        self.valid_dir = False
        self.gui = None

    def run(self, cli: bool = False):
        if cli:
            self.cli()
        else:
            self.gui = MainGUI(self)
            self.gui.mainloop()

    def to_html(self, chat_name: str):
        """Analyzes the chat and creates an HTML output file"""
        chat = self.source.get_chat(chat_name)

        create_new = check_if_create_new(chat.title, len(chat.messages))
        if not create_new:
            return

        analyzer = Analyzer(chat)
        source = analyzer.mrHtml()
        file_path = get_file_path(chat.title)

        with io.open(file_path, "w", encoding="utf-8") as data:
            data.write(source)

        open_html(file_path)

    def to_cli(self, chat_name: str):
        """Analyzes the chat and prints the stats to terminal"""
        chat = self.source.get_chat(chat_name)
        analyzer = Analyzer(chat)

        print(f"Chat: {chat.title}, from {chat.from_day} to {chat.to_day}")
        pprint(
            analyzer.chat_stats(chat.basic_stats, chat.names), indent=2, sort_dicts=True
        )
        pprint(
            analyzer.reaction_stats(chat.reactions, chat.names, chat.people),
            indent=2,
            sort_dicts=False,
        )
        pprint(
            analyzer.emoji_stats(chat.emojis, chat.names, chat.people),
            indent=2,
            sort_dicts=False,
        )
        pprint(analyzer.time_stats(chat.times), indent=2, sort_dicts=False)
        pprint(chat.first_message(), indent=2, sort_dicts=False)

    def cli(self):
        """CLI loop used mainly for testing purposes"""
        self.data_dir_path = os.getcwd()
        try:
            self.source = FacebookMessenger(self.data_dir_path)
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
