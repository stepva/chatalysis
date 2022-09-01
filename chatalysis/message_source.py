import abc


class MessageSource:
    def __init__(self, path: str):
        self.chats = []
        self.data_dir_path = path

    @abc.abstractmethod
    def get_all_chats(self):
        """Extracts all chats in the data folder"""
        pass

    @abc.abstractmethod
    def get_chat(self, chat_name: str) -> "list[str]":
        """Gets a list of specific chats to analyze

        :param chat_name: name of the chat whose information should be analyzed
        """
        pass

    @abc.abstractmethod
    def process_messages(self, messages: list, names: "list[str]", *args):
        """Goes through all the messages and returns Chat object

        :param messages: messages to be analyzed
        :param names: names of the participants
        :return: Chat
        """
        pass

    @abc.abstractmethod
    def to_html(self, chat: "list[str]"):
        """Analyzes the chat and creates HTML output file with stat visualization"""
        pass

    @abc.abstractmethod
    def to_cli(self, chat: "list[str]"):
        """Analyzes the chat and generates a CLI output"""
        pass
