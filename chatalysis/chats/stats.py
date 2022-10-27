import abc
from collections import namedtuple
from dataclasses import dataclass
from datetime import date
from enum import Enum

Times = namedtuple("Times", ["hours", "days", "weekdays", "months", "years"])


class StatsType(Enum):
    REGULAR = 1
    GROUP = 2
    PERSONAL = 3


@dataclass(frozen=True)
class Stats(abc.ABC):
    messages: list
    photos: dict
    gifs: dict
    stickers: dict
    videos: dict
    audios: dict
    files: dict
    reactions: dict
    emojis: dict
    times: Times
    from_day: date
    to_day: date
    people: dict[str, int]  # dict of people who sent messages in the chat and the number of their messages
    participants: list[str]  # list of chat participants
    title: str
    stats_type: StatsType

    @abc.abstractmethod
    def first_message(self) -> dict:
        """Returns the first ever message in the conversation

        :return: dictionary with the first message
        """
        pass


class FacebookStats(Stats):
    """Facebook Messenger / Instagram stats"""

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
