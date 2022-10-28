from datetime import date, datetime
from typing import Any

import emoji
import regex

from chats.stats import FacebookStats, Times, StatsType, SourceType
from sources.facebook_source import FacebookSource
from utils.const import HOURS_DICT


class Instagram(FacebookSource):
    def __init__(self, path: str):
        FacebookSource.__init__(self, path)
        self.source_type = SourceType.INSTAGRAM

    def _process_messages(
        self, messages: list, participants: list[str], title: str, stats_type: StatsType = None
    ) -> FacebookStats:
        """Processes the messages, produces raw stats and stores them in a Chat object.

        :param messages: list of messages to process
        :param participants: list of the chat participants
        :param title: title of the chat
        :param stats_type: type of stats (regular / group chat / overall personal)
        :return: FacebookMessengerChat with the processed chats
        """
        from_day = date.fromtimestamp(messages[0]["timestamp_ms"] // 1000)
        to_day = date.fromtimestamp(messages[-1]["timestamp_ms"] // 1000)
        people = {"total": 0}
        photos = {"total": 0}
        gifs = {"total": 0}
        stickers = {"total": 0}
        videos = {"total": 0}
        audios = {"total": 0}
        files = {"total": 0}
        reactions: Any = {"total": 0, "types": {}, "gave": {}, "got": {}}
        emojis: Any = {"total": 0, "types": {}, "sent": {}}
        days = self._days_list(messages)
        months: dict[str, int] = {}
        years: dict[str, int] = {}
        weekdays: dict[int, int] = {}
        hours = HOURS_DICT.copy()

        for n in participants:
            people[n] = 0
            reactions["gave"][n] = {"total": 0}
            reactions["got"][n] = {"total": 0}
            emojis["sent"][n] = {"total": 0}

        for m in messages:
            name = m["sender_name"]
            day = date.fromtimestamp(m["timestamp_ms"] // 1000)
            days[str(day)] += 1
            month = f"{day.month}/{day.year}"
            months[month] = 1 + months.get(month, 0)
            year = f"{day.year}"
            years[year] = 1 + years.get(year, 0)
            weekday = date.fromtimestamp(m["timestamp_ms"] // 1000).isoweekday()
            weekdays[weekday] = 1 + weekdays.get(weekday, 0)
            hour = datetime.fromtimestamp(m["timestamp_ms"] // 1000).hour
            hours[hour] += 1
            people["total"] += 1
            if name in participants:
                people[name] = 1 + people.get(name, 0)
            if "content" in m:
                if name in participants:
                    emojis = self._extract_emojis(m, emojis)
            elif "photos" in m:
                photos["total"] += 1
                if name in participants:
                    photos[name] = 1 + photos.get(name, 0)
            elif "share" in m:
                if "link" in m["share"] and m["share"]["link"].endswith("gif"):
                    gifs["total"] += 1
                    if name in participants:
                        gifs[name] = 1 + gifs.get(name, 0)
            elif "videos" in m:
                videos["total"] += 1
                if name in participants:
                    videos[name] = 1 + videos.get(name, 0)
            elif "audio_files" in m:
                audios["total"] += 1
                if name in participants:
                    audios[name] = 1 + audios.get(name, 0)
            if "reactions" in m:
                reactions = self._process_reactions(m, name, participants, reactions)

        times = Times(hours, days, weekdays, months, years)

        return FacebookStats(
            messages,
            photos,
            gifs,
            stickers,
            videos,
            audios,
            files,
            reactions,
            emojis,
            times,
            from_day,
            to_day,
            people,
            participants,
            title,
            stats_type,
            self.source_type,
        )
