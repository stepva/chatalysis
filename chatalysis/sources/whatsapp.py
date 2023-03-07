import datetime
import regex
import emoji
from collections import defaultdict

from chats.stats import Times, SourceType, StatsType
from sources.message_source import MessageSource
from chats.stats import Stats
from utils.const import EMOJIS_REGEX, EMOJIS_DICT, TRANSLATE_REMOVE_LETTERS


class WhatsApp(MessageSource):
    """WhatsApp message source for a single conversation (file)"""

    def __init__(self, path: str):
        MessageSource.__init__(self, path)
        self._regex_whatsapp = regex.compile(r"([0-9]*)/([0-9]*)/([0-9]*), ([0-9]*):[0-9]* - ([^:]*):(.*)")
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
            match = self._regex_whatsapp.match(line)

            if match:
                month, day, year, hour, name, message = match.groups()
                date = datetime.date(int(year) + 2000, int(month), int(day))

                dates.append(date)
                days[str(date)] += 1
                months[f"{date.month}/{date.year}"] += 1
                years[str(date.year)] += 1
                weekdays[date.isoweekday()] += 1
                hours[int(hour)] += 1

                people["total"] += 1
                people[name] += 1
                participants.add(name)

            data = line.translate(TRANSLATE_REMOVE_LETTERS)

            text_emoji = self._regex_emoji.search(data)
            if text_emoji:
                data += "".join([EMOJIS_DICT[e] for e in text_emoji.groups()])

            # FIXME the emojis dict has a different structure than the Messenger one.
            #   The Analyzer class needs to be modified to support this dict structure.

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
            emojis=emojis,
            times=times,
            from_day=dates[0],
            to_day=dates[-1],
            people=people,
            participants=list(participants),
            title=None,
            nicknames=None,
            group_names=None,
            stats_type=stats_type,
            source_type=SourceType.WHATSAPP,
        )
