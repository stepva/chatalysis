import abc
from collections import namedtuple
from dataclasses import dataclass
from datetime import date
from enum import Enum

Times = namedtuple("Times", ["hours", "days", "weekdays", "months", "years"])
BasicStats = namedtuple("BasicStats", ["people", "photos", "gifs", "stickers", "videos", "audios", "files"])


class ChatType(Enum):
    REGULAR = 1
    GROUP = 2


@dataclass(frozen=True)
class Chat(abc.ABC):
    messages: list
    basic_stats: BasicStats
    reactions: dict
    emojis: dict
    times: Times
    people: dict[str, int]  # dict of people who sent messages in the chat and the number of their messages
    from_day: date
    to_day: date
    names: list[str]  # list of chat participants
    title: str
    chat_type: ChatType

    @abc.abstractmethod
    def first_message(self) -> dict:
        """Returns the first ever message in the conversation

        :return: dictionary with the first message
        """
        pass


class FacebookMessengerChat(Chat):
    def first_message(self):
        author = self.messages[0]["sender_name"]
        texts = {}
        i = 0
        while True:
            if self.messages[i]["sender_name"] == author:
                texts[self.messages[i]["sender_name"]] = self.messages[i]["content"]
                i += 1
            else:
                texts[self.messages[i]["sender_name"]] = self.messages[i]["content"]
                break
        return texts
