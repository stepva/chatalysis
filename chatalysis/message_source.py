import abc


class MessageSource:
    def __init__(self, path: str):
        self.chats = []
        self.data_dir_path = path

    @abc.abstractmethod
    def get_all_chats(self) -> list:
        """Extracts all chats in the data folder"""
        pass

    @abc.abstractmethod
    def get_chat(self, chat_name: str):
        """Gets all chat information for a specific chat

        :param chat_name: name of the chat whose information should be analyzed
        """
        pass
