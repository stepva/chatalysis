import io
from typing import Any

from chats.analyzer import Analyzer
from chats.stats import Stats
from gui.main_gui import MainGUI
from utils.utility import get_file_path, open_html
from utils.config import Config


class Program:
    def __init__(self) -> None:
        self.source: Any = None
        self.gui: Any = None

        self.config = Config()
        self.print_stacktrace = self.config.load("print_stacktrace", "dev", is_bool=True)

        self.data_dir_path = ""
        self.valid_dir = False

    def run(self) -> None:
        self.gui = MainGUI(self)
        self.gui.mainloop()

    def chat_to_html(self, name: str) -> Any:
        chat = self.source.get_chat(name)
        self.to_html(chat)

    def to_html(self, chat: Stats) -> None:
        """Analyzes any type of chat (or PersonalStats), creates an HTML output file and opens it in the browser.

        :param chat: Chat or PersonalStats to analyze
        """
        output_file = get_file_path(chat.title, self.source.__class__.__name__)

        analyzer = Analyzer(chat)
        source = analyzer.create_html()

        with io.open(output_file, "w", encoding="utf-8") as data:
            data.write(source)

        open_html(output_file)
