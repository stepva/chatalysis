import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from statistics import mode

import emoji
import regex
from chatalysis.chats.personal import PersonalStats

from chats.chat import BasicStats, ChatType, FacebookMessengerChat, Times
from sources.message_source import MessageSource
from utils.const import HOURS_DICT

chat_id_str = str  # alias for str that denotes a unique chat ID (for example: "johnsmith_djnas32owkldm")


class FacebookMessenger(MessageSource):
    def __init__(self, path: str):
        MessageSource.__init__(self, path)
        self.folders = []
        self.chat_ids = []  # list of all conversations identified by their chat ID

        # Mapping of condensed conversation names (user input) to chat IDs. Since a conversation name
        # can represent multiple chats, the chat IDs are stored in a list.
        self.chat_id_map: dict[str, list[chat_id_str]] = {}

        # Intermediate cache of the extracted but not yet processed messages. The values stored are tuples of
        # messages, names of the chat participants, chat title and chat type. Once the messages have been processed,
        # they are removed from this cache as they can be accessed via the Chat object.
        self.messages_cache: dict[chat_id_str, tuple[list, list, str, ChatType]] = {}

        # cache of Chat objects
        self.chats_cache: dict[chat_id_str, FacebookMessengerChat] = {}

        self._load_message_folders()
        self._load_all_chats()
        self._check_media()

    # region Public API

    def get_chat(self, chat_name: str) -> FacebookMessengerChat:
        possible_chat_ids = self.chat_id_map[chat_name]

        # Check for chat collisions
        if len(possible_chat_ids) == 1:
            chat_id = possible_chat_ids[0]
        else:
            # TODO create a GUI dialog for this case
            print(f"There are {len(possible_chat_ids)} different chats with this name:")
            self._multiple_chats(possible_chat_ids)
            i = int(input("Which one do you want? ")) - 1
            chat_id = possible_chat_ids[i]

        if chat_id not in self.chats_cache:
            self._compile_chat_data(chat_id)
        return self.chats_cache[chat_id]

    def personal_stats(self) -> PersonalStats:
        messages = []
        names = []  # list of participants from all conversations

        for chat_id in self.chat_ids:
            if chat_id in self.chats_cache:
                messages.extend(self.chats_cache[chat_id].messages)
                names.extend(self.chats_cache[chat_id].names)
            elif chat_id in self.messages_cache:
                messages.extend(self.messages_cache[chat_id][0])
                names.extend(self.messages_cache[chat_id][1])
            else:
                # extract data for the chat and cache it
                self.messages_cache[chat_id] = self._prepare_chat_data(chat_id)
                messages.extend(self.messages_cache[chat_id][0])
                names.extend(self.messages_cache[chat_id][1])

        # find the user's name (the one that appears in all conversations)
        name = mode(names)

        messages = [m for m in messages if m["sender_name"] == name]
        messages = sorted(messages, key=lambda k: k["timestamp_ms"])
        return self._process_messages(messages, [name], "Personal stats", None, personal_stats=True)

    def top_ten(self):
        chats = {}
        groups = {}

        for chat_id in self.chat_ids:
            if chat_id in self.chats_cache:
                title = self.chats_cache[chat_id].title
                chat_type = self.chats_cache[chat_id].chat_type
                messages = self.chats_cache[chat_id].messages
            elif chat_id in self.messages_cache:
                messages, _, title, chat_type = self.messages_cache[chat_id]
            else:
                # extract data for the chat and cache it
                messages, participants, title, chat_type = self._prepare_chat_data(chat_id)
                self.messages_cache[chat_id] = messages, participants, title, chat_type

            # remove emoji because it ruins the aligning of the output text
            title = emoji.replace_emoji(title, "")

            if chat_type == ChatType.REGULAR:
                chats[title] = len(messages)
            elif chat_type == ChatType.GROUP:
                groups[title] = len(messages)

        top_individual = dict(sorted(chats.items(), key=lambda item: item[1], reverse=True)[0:10])
        top_group = dict(sorted(groups.items(), key=lambda item: item[1], reverse=True)[0:5])
        return top_individual, top_group

    # endregion

    # region Chat processing

    def _compile_chat_data(self, chat_id: str):
        """Gets all the chat data, processes it and stores it as a Chat object in the cache.

        :param chat_id: name of the chat to process
        """
        if chat_id in self.messages_cache:
            # fetch unprocessed extracted data
            messages, participants, title, chat_type = self.messages_cache[chat_id]
            self.messages_cache.pop(chat_id)
        else:
            messages, participants, title, chat_type = self._prepare_chat_data(chat_id)

        self.chats_cache[chat_id] = self._process_messages(messages, participants, title, chat_type)

    def _prepare_chat_data(self, chat_id: str) -> tuple[list, list, str, ChatType]:
        """Extracts the chat data (messages, names of the participants, chat title and chat type)

        :param chat_id: name of the chat to process
        :return: messages - list of messages
                 title - name of the conversation,
                 participants - names of conversation participants
                 chat_type - type of chat (regular chat, group chat)
        """
        chat_paths = self._get_paths(chat_id)
        jsons = self._get_jsons(chat_paths)
        messages = []

        first = True
        for json_file in jsons:
            with open(json_file, "r") as data:
                data = json.load(data)
                messages.extend(data["messages"])

                if first:
                    # get title, participants and chat type, which are the same across all JSONs
                    title = self._decode(data["title"])
                    participants = self._get_participants(data)

                    if data["thread_type"] == "RegularGroup":
                        chat_type = ChatType.GROUP
                    else:
                        chat_type = ChatType.REGULAR

                    first = False

        messages = sorted(messages, key=lambda k: k["timestamp_ms"])
        self._decode_messages(messages)
        return messages, participants, title, chat_type

    def _get_paths(self, chat_id: str) -> list[Path]:
        """Gets paths to the inbox folders with desired chat.

        :param chat_id: chat ID of the desired chat
        :return: list of paths to the inbox folders
        """
        paths = []

        for folder in self.folders:
            path_name = f"{folder}/inbox/{chat_id}"
            if os.path.isdir(path_name):
                paths.append(Path(path_name))

        return paths

    @staticmethod
    def _get_jsons(chat_paths: list[Path]) -> list[Path]:
        """Gets the json(s) with messages for a particular chat

        :param chat_paths: list of paths to the inbox folders of the chat
        :return: list of JSON files with the messages
        """
        jsons = []

        for ch in chat_paths:
            for file in os.listdir(ch):
                if str(file).startswith("message") and str(file).endswith(".json"):
                    jsons.append(ch / str(file))
        if not jsons:
            raise Exception("No JSON files in this chat")

        return jsons

    def _get_participants(self, chat: dict) -> list[str]:
        """Gets names of the participants in the chat.

        :param chat: raw chat data
        :return: list of chat participants
        """
        participants = []
        for i in chat["participants"]:
            participants.append(self._decode(i["name"]))
        if len(participants) == 1:
            participants.append(participants[0])
        return participants

    def _process_messages(
        self, messages: list, names: list[str], title: str, chat_type: ChatType, personal_stats: bool = False
    ) -> FacebookMessengerChat | PersonalStats:
        """Processes the messages, produces raw stats and stores them in a Chat object.
        :param messages: list of messages to process
        :param names: list of the chat participants
        :param title: title of the chat
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

        for n in names:
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
            if name in names:
                people[name] = 1 + people.get(name, 0)
            if "content" in m:
                if name in names:
                    data = regex.findall(r"\X", m["content"])
                    for c in data:
                        if c in emoji.EMOJI_DATA:
                            emojis["total"] += 1
                            emojis["types"][c] = 1 + emojis["types"].get(c, 0)
                            emojis["sent"][name]["total"] += 1
                            emojis["sent"][name][c] = 1 + emojis["sent"][name].get(c, 0)
            elif "photos" in m:
                photos["total"] += 1
                if name in names:
                    photos[name] = 1 + photos.get(name, 0)
            elif "gifs" in m:
                gifs["total"] += 1
                if name in names:
                    gifs[name] = 1 + gifs.get(name, 0)
            elif "sticker" in m:
                stickers["total"] += 1
                if name in names:
                    stickers[name] = 1 + stickers.get(name, 0)
            elif "videos" in m:
                videos["total"] += 1
                if name in names:
                    videos[name] = 1 + videos.get(name, 0)
            elif "audio_files" in m:
                audios["total"] += 1
                if name in names:
                    audios[name] = 1 + audios.get(name, 0)
            elif "files" in m:
                files["total"] += 1
                if name in names:
                    files[name] = 1 + files.get(name, 0)
            if "reactions" in m:
                for r in m["reactions"]:
                    if r["reaction"] == self._decode("\u00e2\u009d\u00a4"):
                        reaction = "❤️"
                    else:
                        reaction = r["reaction"]
                    reactions["total"] += 1
                    reactions["types"][reaction] = 1 + reactions["types"].get(reaction, 0)
                    if name in names:
                        reactions["got"][name]["total"] += 1
                        reactions["got"][name][reaction] = 1 + reactions["got"][name].get(reaction, 0)
                        if r["actor"] in names:
                            reactions["gave"][r["actor"]]["total"] += 1
                            reactions["gave"][r["actor"]][reaction] = 1 + reactions["gave"][r["actor"]].get(reaction, 0)

        basic_stats = BasicStats(people, photos, gifs, stickers, videos, audios, files)
        times = Times(hours, days, weekdays, months, years)

        if personal_stats:
            return PersonalStats(
                names, messages, basic_stats, reactions, emojis, times, people, from_day, to_day, title
            )
        else:
            return FacebookMessengerChat(
                messages, basic_stats, reactions, emojis, times, people, from_day, to_day, names, title, chat_type
            )

    # endregion

    # region Data source processing

    def _load_message_folders(self):
        """Load folders containing the messages"""
        for d in os.listdir(self.data_dir_path):
            if d.startswith("messages") and os.path.isdir(f"{self.data_dir_path}/{d}"):
                self.folders.append(f"{self.data_dir_path}/{d}")

        if not self.folders:
            raise Exception(
                'Looks like there is no "messages" folder here. Make sure to add the "messages" folder downloaded from '
                "Facebook as described in the README :)"
            )

    def _load_all_chats(self):
        """Load all chats from the source"""
        for folder in self.folders:
            for chat_id in os.listdir(Path(folder) / "inbox"):
                if chat_id != ".DS_Store":
                    name = str(chat_id).split("_")[0].lower()

                    if name not in self.chat_id_map:
                        self.chat_id_map[name] = [str(chat_id).lower()]
                    else:
                        previous_id = self.chat_id_map[name][0]
                        if chat_id != previous_id:
                            self.chat_id_map[name].append(str(chat_id).lower())

                    self.chat_ids.append(chat_id)

    def _check_media(self):
        """Checks if all media types are included, as for some users Facebook doesn’t include files or videos"""
        media = {"photos": 0, "videos": 0, "files": 0, "gifs": 0, "audio": 0}

        for folder in self.folders:
            everything = []
            for _, dirs, _ in os.walk(folder):
                everything.extend(dirs)
            for i in media.keys():
                if i in everything:
                    media[i] = 1

        no_media = [m for m in media.keys() if media[m] == 0]

        no_media_str = ", ".join(no_media)
        if no_media:
            raise Exception(
                f"These media types are not included in your messages for some reason: {no_media_str}."
                "I can’t do anything about it.\n"
            )

    # endregion

    # region Facebook-specific utilities

    @staticmethod
    def _decode(word: str) -> str:
        """Decodes a string from the Facebook encoding."""
        return word.encode("iso-8859-1").decode("utf-8")

    @staticmethod
    def _decode_messages(messages):
        """Decodes all messages from the Facebook encoding"""
        for m in messages:
            m["sender_name"] = m["sender_name"].encode("iso-8859-1").decode("utf-8")
            if "content" in m:
                m["content"] = m["content"].encode("iso-8859-1").decode("utf-8")
            if "reactions" in m:
                for r in m["reactions"]:
                    r["reaction"] = r["reaction"].encode("iso-8859-1").decode("utf-8")
                    r["actor"] = r["actor"].encode("iso-8859-1").decode("utf-8")
        return messages

    @staticmethod
    def _days_list(messages: list) -> "dict[str, int]":
        """Prepares a dictionary with all days from the first message up to the last one

        :param messages: list of messages in the conversation
        :return: dictionary of days
        """
        from_day = date.fromtimestamp(messages[0]["timestamp_ms"] // 1000)
        to_day = date.fromtimestamp(messages[-1]["timestamp_ms"] // 1000)
        delta = to_day - from_day
        days = {}
        for i in range(delta.days + 1):
            day = from_day + timedelta(days=i)
            days[str(day)] = 0
        return days

    # endregion

    def _multiple_chats(self, chat_ids):
        """Gets information about chats with the same name"""
        chat_paths = {}
        jsons = {}
        names = {}
        lengths = {}

        for chat_id in chat_ids:
            chat_paths[chat_id] = self._get_paths(chat_id)
            jsons[chat_id], _, names[chat_id], _ = self._get_jsons_title_names(chat_paths[chat_id])
            lengths[chat_id] = [(len(jsons[chat_id]) - 1) * 10000, len(jsons[chat_id]) * 10000]
            print(
                f"{chat_ids.index(chat_id)+1}) with {names[chat_id]} and {lengths[chat_id][0]}-{lengths[chat_id][1]} messages"
            )
