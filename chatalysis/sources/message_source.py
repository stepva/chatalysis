from __future__ import annotations
import abc
from pathlib import Path

from chats.stats import Stats


class NoMessageFilesError(RuntimeError):
    pass


class MessageSource(abc.ABC):
    """Abstract class for a message source, which loads all available conversations
    and extracts them into Chat objects upon request."""

    def __init__(self, path: str):
        super().__init__()
        self._data_path = Path(path)

    @abc.abstractmethod
    def get_chat(self, chat_name: str) -> Stats:
        """Extracts an individual chat. If there are colliding chats with the same name,
        extracts one of the possible chats, based on the user's choice.

        :param chat_name: name of the chat to extract
        :return: desired chat as a Chat object (chat class inherited from Chat)
        """

    @abc.abstractmethod
    def conversation_size(self, chat: str) -> int:
        """Gets amount of messages in a conversation.

        :param chat: name of the conversation / chat ID
        """
