from collections import namedtuple
from dataclasses import dataclass
from datetime import date

from chatalysis.chats.chat import ChatType

Times = namedtuple("Times", ["hours", "days", "weekdays", "months", "years"])
BasicStats = namedtuple("BasicStats", ["people", "photos", "gifs", "stickers", "videos", "audios", "files"])

# todo tohtml in analyzer, probably separate fce for personal_html
@dataclass
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
    chat_type: ChatType = ChatType.PERSONAL_STATS
