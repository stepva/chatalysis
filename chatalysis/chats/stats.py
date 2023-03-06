import abc
from collections import namedtuple
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto
from typing import Any

Times = namedtuple("Times", ["hours", "days", "weekdays", "months", "years"])


class StatsType(Enum):
    REGULAR = auto()
    GROUP = auto()
    PERSONAL = auto()


class SourceType(Enum):
    MESSENGER = auto()
    INSTAGRAM = auto()
    WHATSAPP = auto()


@dataclass(frozen=True)
class Stats(abc.ABC):
    # fmt: off
    messages:       list[Any] | None
    photos:         dict[Any, Any] | None
    gifs:           dict[Any, Any] | None
    stickers:       dict[Any, Any] | None
    videos:         dict[Any, Any] | None
    audios:         dict[Any, Any] | None
    files:          dict[Any, Any] | None
    reactions:      dict[Any, Any] | None
    emojis:         dict[Any, Any] | None
    times:          Times
    from_day:       date
    to_day:         date
    people:         dict[str, int]  # dict of people who sent messages in the chat and the number of their messages
    participants:   list[str]  # list of chat participants
    title:          str | None
    nicknames:      list[dict[str, Any]] | None
    group_names:    list[dict[str, Any]] | None
    stats_type:     StatsType
    source_type:    SourceType
    # avg_message_lengths: dict[Any, Any]
    # longest_message: dict[Any, Any]
    # fmt: on


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
