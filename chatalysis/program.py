import io
from pprint import pprint
from gui import MainGUI
from analyzer import Analyzer
from utility import open_html, get_file_path, check_if_create_new


class Program:
    def __init__(self):
        self.source = None
        self.top_ten_individual = None
        self.top_five_groups = None
        self.data_dir_path = ""
        self.valid_dir = False
        self.gui = MainGUI(self)

    def run(self):
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
        pprint(analyzer.chat_stats(chat.basic_stats, chat.names), indent=2, sort_dicts=True)
        pprint(analyzer.reaction_stats(chat.reactions, chat.names, chat.people), indent=2, sort_dicts=False)
        pprint(analyzer.emoji_stats(chat.emojis, chat.names, chat.people), indent=2, sort_dicts=False)
        pprint(analyzer.time_stats(chat.times), indent=2, sort_dicts=False)
        pprint(self.source.first_message(chat.messages), indent=2, sort_dicts=False)
