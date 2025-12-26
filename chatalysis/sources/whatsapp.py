import datetime
import regex
import emoji
from collections import defaultdict
from typing import Any

import dateparser

from chats.stats import Times, SourceType, StatsType
from sources.message_source import MessageSource
from chats.stats import Stats
from utils.const import EMOJIS_REGEX, EMOJIS_DICT, TRANSLATE_REMOVE_LETTERS


# WhatsApp export files can have different formats including different delimiters. These two patterns
# cover the formats that we've encountered so far, although it is likely there are many more formats :(
WHATSAPP_REGEXES = [
    regex.compile(r"^([^[]+?)\s[-~]\s(.+):\s(.+)"),   # "3/30/24, 15:55 - name: message"
    regex.compile(r"^\[(.+?)\][\s]+(.+):\s(.+)")  # "[13.06.2023, 18:08:08] name: message"
]

WHATSAPP_CHAT_NAME_REGEX = regex.compile(r"WhatsApp Chat with (.+)")


class WhatsApp(MessageSource):
    """WhatsApp message source for a single conversation (file)."""

    def __init__(self, path: str):
        MessageSource.__init__(self, path)
        self._regex_emoji = regex.compile(EMOJIS_REGEX)

        self._messages = self._process_messages()

    # region Public API

    def get_chat(self, _: str) -> Stats:
        """Extracts the chat.

        :param _: dummy parameter to satisfy the parent method signature
        :return: desired chat as a Chat object
        """
        return self._messages

    def conversation_size(self, _: str) -> int:
        """Gets number of messages in the conversation.

        :param _: dummy parameter to satisfy the parent method signature
        :return: desired chat as a Chat object
        """
        return self._messages.people["total"]

    # endregion

    def _process_messages(self) -> Stats:
        with open(self._data_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        name = ""
        participants = set()
        people: dict[str, int] = defaultdict(int)
        emojis: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

        days: dict[str, int] = defaultdict(int)
        months: dict[str, int] = defaultdict(int)
        years: dict[str, int] = defaultdict(int)
        weekdays: dict[int, int] = defaultdict(int)
        hours: dict[int, int] = defaultdict(int)
        dates = []

        for line in lines:
            ret = self._parse_line(line)

            if ret:
                dt, name, message = ret

                dates.append(dt.date())
                days[str(dt.date())] += 1
                months[f"{dt.month}/{dt.year}"] += 1
                years[str(dt.year)] += 1
                weekdays[dt.isoweekday()] += 1
                hours[int(dt.hour)] += 1

                people["total"] += 1
                people[name] += 1
                participants.add(name)

            data = line.translate(TRANSLATE_REMOVE_LETTERS)

            text_emoji = self._regex_emoji.search(data)
            if text_emoji:
                data += "".join([EMOJIS_DICT[e] for e in text_emoji.groups()])

            # Remaining lines of multiline messages are not matched by the regex (only the first line is)
            # but their content is still analyzed for emoji and the emoji are attributed to the last name
            # matched by the regex. There might be some edge case that will break this, but it works for now.
            for c in data:
                if c in emoji.EMOJI_DATA:
                    emojis["total"]["total"] += 1
                    emojis["total"][c] += 1
                    emojis[name]["total"] += 1
                    emojis[name][c] += 1

        times = Times(hours, days, weekdays, months, years)
        stats_type = StatsType.PERSONAL if len(participants) == 2 else StatsType.GROUP

        return Stats(
            messages=None,
            photos=None,
            gifs=None,
            stickers=None,
            videos=None,
            audios=None,
            files=None,
            reactions=None,
            emojis=self._reshape_emoji_dict(emojis),
            times=times,
            from_day=dates[0],
            to_day=dates[-1],
            people=people,
            participants=list(participants),
            title=self._get_chat_name(),
            nicknames=None,
            group_names=None,
            stats_type=stats_type,
            source_type=SourceType.WHATSAPP,
        )

    @staticmethod
    def _reshape_emoji_dict(emoji_dict: dict[Any, Any]) -> dict[Any, Any]:
        """Change the dict structure to be the same as used in the rest of the program.

        :param emoji_dict: dict with emoji to restructure
        :return: restructured dict
        """
        return {
            "total": emoji_dict["total"]["total"],
            "types": {k: v for k, v in emoji_dict["total"].items() if k != "total"},
            "sent": {k: dict(v) for k, v in emoji_dict.items() if k != "total"}
        }

    @staticmethod
    def _parse_line(line: str) -> tuple[datetime.datetime, str, str] | None:
        """Try parsing a date, name and message from a line. Since the lines can have different formats,
        the function tries matching using different regexes.

        :param line: Line to parse.
        :return: Return a tuple of (datetime object, name, message) if the message was successfully parsed. If no
            regex matched the string or the date could not be parsed, None is returned.
        """
        for pattern in WHATSAPP_REGEXES:
            m = regex.match(pattern, line)
            if m:
                datetime_str, name, message = m.groups()
                dt = dateparser.parse(datetime_str)  # try parsing the extracted date string

                if dt is not None:
                    return dt, name, message
        return None

    def _get_chat_name(self) -> str:
        """Get name of the chat if the source file follows the standard naming convention 'WhatsApp Chat with <NAME>'.

        :return: Name of the chat if it was successfully parsed, 'WhatsApp chat' otherwise.
        """
        m = regex.match(WHATSAPP_CHAT_NAME_REGEX, self._data_path.stem)
        return m.group(1) if m else "WhatsApp chat"
