import datetime
import regex
from collections import defaultdict

from chats.stats import Times, SourceType, StatsType
from sources.message_source import MessageSource
from chats.stats import Stats


class WhatsApp(MessageSource):
    """WhatsApp message source for a single conversation (file)"""

    def __init__(self, path: str):
        MessageSource.__init__(self, path)
        self._regex_whatsapp = regex.compile(r"([0-9]*)/([0-9]*)/([0-9]*), ([0-9]*):[0-9]* - ([^:]*):(.*)")
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

        people: dict[str, int] = defaultdict(int)
        participants = set()

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
            emojis=None,
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
