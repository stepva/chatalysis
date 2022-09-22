import abc
from collections import namedtuple
from dataclasses import dataclass
from datetime import date
from typing import Any

Times = namedtuple("Times", ["hours", "days", "weekdays", "months", "years"])
BasicStats = namedtuple("BasicStats", ["people", "photos", "gifs", "stickers", "videos", "audios", "files"])


@dataclass # type: ignore[misc]
class Chat(abc.ABC):
    messages: list[Any]
    basic_stats: BasicStats
    reactions: dict[Any, Any]
    emojis: dict[Any, Any]
    times: Times
    people: dict[Any, Any]
    from_day: date
    to_day: date
    names: list[str]
    title: str

    @abc.abstractmethod
    def first_message(self) -> dict[Any, Any]:
        """Returns the first ever message in the conversation

        :return: dictionary with the first message
        """
        pass


class FacebookMessengerChat(Chat):
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
