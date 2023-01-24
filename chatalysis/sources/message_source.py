from __future__ import annotations
import abc
from pathlib import Path
from typing import Any, TYPE_CHECKING

from chats.stats import Stats
if TYPE_CHECKING:
    from gui.main_gui import MainGUI


class NoMessageFilesError(RuntimeError):
    pass


class MessageSource(abc.ABC):
    """Abstract class for a message source, which loads all available conversations
    and extracts them into Chat objects upon request."""

    def __init__(self, path: str):
        super().__init__()
        self._data_dir_path = Path(path)

    @abc.abstractmethod
    def get_chat(self, chat_name: str) -> Stats:
        """Extracts an individual chat. If there are colliding chats with the same name,
        extracts one of the possible chats, based on the user's choice.

        :param chat_name: name of the chat to extract
        :return: desired chat as a Chat object (chat class inherited from Chat)
        """

    @abc.abstractmethod
    def personal_stats(self, gui: MainGUI = None) -> Stats:
        """Gets overall personal stats (stats across all available conversations)

        :param gui: main GUI displaying the progress bar
        :return: Stats object with the personal stats
        """

    @abc.abstractmethod
    def top_ten(self) -> tuple[list[Any], list[Any]]:
        """Gets the top 10 individual chats and top 5 group chats based on number of messages.

        :return: dictionary of top 10 individual conversations & top 5 group chats
                 with the structure {conversation name: number of messages}
        """

    @abc.abstractmethod
    def conversation_size(self, chat: str) -> int:
        """Gets amount of messages in a conversation.

        :param chat: name of the conversation / chat ID
        """
