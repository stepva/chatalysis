from datetime import date, datetime
from typing import Any
from statistics import mean
import regex

from chats.stats import StatsType, FacebookStats, Times, SourceType
from sources.facebook_source import FacebookSource
from utils.const import HOURS_DICT


class Messenger(FacebookSource):
    def __init__(self, path: str):
        FacebookSource.__init__(self, path)
        self.source_type = SourceType.MESSENGER

    def _process_messages(
        self, messages: list[Any], participants: list[str], title: str, stats_type: StatsType = None
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
        message_lengths: dict[str, list[int]] = {}  # list of message lengths (in words) from a given person
        total_call_duration = 0

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
            message_lengths[n] = []

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

                # todo get identity from autofill_information.json when loading folders (from the most recent one)
                if "set the nickname for" in m["content"] or "set your nickname to" in m["content"]:
                    print(
                        regex.search(
                            r"(?:set the nickname for |set your nickname)(.*)(?: to )(.+)[.]$", m["content"]
                        ).groups()
                    )

                if name in participants:
                    if m["type"] == "Call":
                        total_call_duration += int(m["call_duration"])
                        continue

                    emojis = self._extract_emojis(m, emojis)
                    words_cnt = len(regex.findall(r"(\b[^\s]+\b)", m["content"]))  # length of the message in words
                    message_lengths[name].append(words_cnt)
            elif "photos" in m:
                photos["total"] += 1
                if name in participants:
                    photos[name] = 1 + photos.get(name, 0)
            elif "gifs" in m:
                gifs["total"] += 1
                if name in participants:
                    gifs[name] = 1 + gifs.get(name, 0)
            elif "sticker" in m:
                stickers["total"] += 1
                if name in participants:
                    stickers[name] = 1 + stickers.get(name, 0)
            elif "videos" in m:
                videos["total"] += 1
                if name in participants:
                    videos[name] = 1 + videos.get(name, 0)
            elif "audio_files" in m:
                audios["total"] += 1
                if name in participants:
                    audios[name] = 1 + audios.get(name, 0)
            elif "files" in m:
                files["total"] += 1
                if name in participants:
                    files[name] = 1 + files.get(name, 0)
            if "reactions" in m:
                reactions = self._process_reactions(m, name, participants, reactions)

        times = Times(hours, days, weekdays, months, years)
        # todo mean requires at least one datapoint
        # avg_message_lengths = {name: round(mean(lengths), 2) for name, lengths in message_lengths.items()}
        # longest_message = {name: sorted(lengths)[-1] for name, lengths in message_lengths.items()}
        avg_message_lengths = {}
        longest_message = {}

        return FacebookStats(
            messages,
            avg_message_lengths,
            longest_message,
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
            total_call_duration // 60,
            stats_type,
            self.source_type,
        )
