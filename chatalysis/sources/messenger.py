from datetime import date, datetime
from typing import Any
from pathlib import Path
import os
import json
import regex

from chats.stats import StatsType, FacebookStats, Times, SourceType
from sources.facebook_source import FacebookSource
from utils.const import HOURS_DICT


class Messenger(FacebookSource):
    def __init__(self, path: str):
        FacebookSource.__init__(self, path)
        self.source_type = SourceType.MESSENGER
        self.user_name = self._get_user_name()

        self.group_names_regex = regex.compile(r"(?:named the group )(.*)[.]$")

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
        nicknames_regex_prep = f"(?:set the nickname for |set your nickname)(|{'|'.join(participants)})(?: to )(.+)[.]$"
        nicknames_regex = regex.compile(nicknames_regex_prep)

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
        nicknames: list[dict[str, Any]] = []
        group_names: list[dict[str, Any]] = []

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
                found, new_nickname = self._process_nicknames(m, nicknames_regex)
                if found:
                    nicknames.append(new_nickname)
                    continue

                if stats_type == StatsType.GROUP:
                    found, new_group_name = self._process_group_names(m)
                    if found:
                        group_names.append(new_group_name)
                        continue

                if name in participants:
                    if m["type"] == "Call":
                        total_call_duration += int(m["call_duration"])
                        continue

                    emojis = self._extract_emojis(m, emojis)
                    # kept here for later
                    # words_cnt = len(regex.findall(r"(\b[^\s]+\b)", m["content"]))  # length of the message in words
                    # message_lengths[name].append(words_cnt)
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

        # kept here for later, but beware - mean requires at least one datapoint
        # avg_message_lengths = {name: round(mean(lengths), 2) for name, lengths in message_lengths.items()}
        # longest_message = {name: sorted(lengths)[-1] for name, lengths in message_lengths.items()}
        # avg_message_lengths = {}
        # longest_message = {}

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
            total_call_duration // 60,
            nicknames,
            group_names,
            stats_type,
            self.source_type,
        )

    def _process_nicknames(
        self, message: dict[Any, Any], nicknames_regex: regex.Pattern
    ) -> tuple[bool, dict[str, Any]]:
        data = nicknames_regex.search(message["content"])
        if data:
            target, nickname = data.groups()
            if target == "":
                target = self.user_name
            return True, {
                "timestamp": message["timestamp_ms"],
                "target": target,
                "nickname": nickname,
                "changed_by": message["sender_name"],
            }

        else:
            return False, {}

    def _process_group_names(self, message: dict[Any, Any]) -> tuple[bool, dict[str, Any]]:
        data = self.group_names_regex.search(message["content"])
        if data:
            group_name = data.groups()
            return True, {
                "timestamp": message["timestamp_ms"],
                "group_name": group_name[0],
                "changed_by": message["sender_name"],
            }

        else:
            return False, {}

    def _get_user_name(self) -> str:
        """Gets the full name of the user from metadata files downloaded with Facebook Messenger messages"""
        info_files = [
            Path(root, f)
            for root, _, files in os.walk(self._data_dir_path)
            for f in files
            if f == "autofill_information.json"
        ]
        info_files_mod_times = [os.path.getmtime(i) for i in info_files]
        idx = max(range(len(info_files_mod_times)), key=info_files_mod_times.__getitem__)

        with open(info_files[idx], "r") as data_file:
            data = json.load(data_file)

        return self._decode(data["autofill_information_v2"]["FULL_NAME"][0])
