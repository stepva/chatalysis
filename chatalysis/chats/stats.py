import abc
from collections import namedtuple
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

Times = namedtuple("Times", ["hours", "days", "weekdays", "months", "years"])


class StatsType(Enum):
    REGULAR = 1
    GROUP = 2
    PERSONAL = 3


class SourceType(Enum):
    MESSENGER = 1
    INSTAGRAM = 2


@dataclass(frozen=True) # type: ignore
class Stats(abc.ABC):
    messages: list[Any]
    photos: dict[Any, Any]
    gifs: dict[Any, Any]
    stickers: dict[Any, Any]
    videos: dict[Any, Any]
    audios: dict[Any, Any]
    files: dict[Any, Any]
    reactions: dict[Any, Any]
    emojis: dict[Any, Any]
    times: Times
    from_day: date
    to_day: date
    people: dict[str, int]  # dict of people who sent messages in the chat and the number of their messages
    participants: list[str]  # list of chat participants
    title: str
    stats_type: StatsType
    source_type: SourceType

    @abc.abstractmethod
    def first_message(self) -> dict[Any, Any]:
        """Returns the first ever message in the conversation

        :return: dictionary with the first message
        """
        pass


class FacebookStats(Stats):
    """Facebook Messenger / Instagram stats"""

    def first_message(self) -> Any:
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
