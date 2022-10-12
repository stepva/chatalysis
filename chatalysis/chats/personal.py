from collections import namedtuple
from dataclasses import dataclass
from datetime import date

from chats.chat import Times, BasicStats


@dataclass(frozen=True)
class PersonalStats:
    names: list[str]  # will only include one name, but it is easier when using other methods for chat
    messages: list
    basic_stats: BasicStats
    reactions: dict
    emojis: dict
    times: Times
    people: dict[str, int]  # dict of people who sent messages in the chat and the number of their messages
    from_day: date
    to_day: date
    title: str
