import abc

from chats.chat import Chat


class MessageSource(abc.ABC):
    """Abstract class for a message source, which loads all available conversations
    and extracts them into Chat objects upon request."""

    def __init__(self, path: str):
        super().__init__()
        self.data_dir_path = path

    @abc.abstractmethod
    def get_chat(self, chat_name: str) -> Chat:
        """Extracts an individual chat. If there are colliding chats with the same name,
        extracts one of the possible chats, based on the user's choice.

        :param chat_name: name of the chat to extract
        :return: desired chat as a Chat object (chat class inherited from Chat)
        """

    @abc.abstractmethod
    def top_ten(self) -> "tuple[dict[str, int], dict[str, int]]":
        """Goes through conversations and returns the top 10 individual chats
        and top 5 group chats based on number of messages.

        :return: dictionary of top 10 individual conversations & top 5 group chats
                 with the structure {conversation name: number of messages}
        """
