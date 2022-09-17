import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import emoji
import regex

from chatalysis.chats.chat import BasicStats, FacebookMessengerChat, Times
from chatalysis.sources.message_source import MessageSource
from chatalysis.utils.const import HOURS_DICT

# chat ID example = "johnsmith_djnas32owkldm"


class FacebookMessenger(MessageSource):
    def __init__(self, path: str):
        MessageSource.__init__(self, path)
        self.folders = []

        # Mapping of condensed conversation names (user input) to chat IDs. Since a conversation name
        # can represent multiple chats, the chat IDs are stored in a list.
        self.chat_ids: dict[str, list[str]] = {}

        # cache of Chat objects
        self.chats_cache: dict[str, FacebookMessengerChat] = {}

        self._load_message_folders()
        self._load_all_chats()
        self._check_media()

    # region Public API

    def get_chat(self, chat_name: str) -> FacebookMessengerChat:
        possible_chat_ids = self.chat_ids[chat_name]

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

    def top_ten(self):
        chats = {}
        groups = {}
        inboxes = [f"{folder}/inbox/" for folder in self.folders]
        names = [i + n for i in inboxes for n in os.listdir(i) if os.path.isdir(i + n)]

        for n in names:
            for file in os.listdir(n):
                if file.startswith("message") and file.endswith(".json"):
                    with open(n + "/" + file) as data:
                        data = json.load(data)

                        # get the "real" name of the individual conversation (as opposed to the "condensed"
                        # format in the folder name (represented here by the variable "m"))
                        conversationName = self._decode(data["title"])
                        # remove emoji because it ruins the aligning of the output text
                        conversationName = emoji.replace_emoji(conversationName, "")

                        if data["thread_type"] == "Regular":
                            chats[conversationName] = len(data["messages"]) + chats.get(conversationName, 0)
                        elif data["thread_type"] == "RegularGroup":
                            groups[conversationName] = len(data["messages"]) + groups.get(conversationName, 0)

                        # if data["messages"][0]["timestamp_ms"] > ts:
                        #     ts = data["messages"][0]["timestamp_ms"]

        top_individual = dict(sorted(chats.items(), key=lambda item: item[1], reverse=True)[0:10])
        top_group = dict(sorted(groups.items(), key=lambda item: item[1], reverse=True)[0:5])
        return top_individual, top_group

    # endregion

    # region Chat processing

    def _compile_chat_data(self, chat_name: str):
        """Gets all the chat data, processes it and stores it as a Chat object in the cache.

        :param chat_name: name of the chat to process
        """
        chat_paths = self._get_paths(chat_name)
        jsons, title, names = self._get_jsons_title_names(chat_paths)
        messages = self._get_messages(jsons)

        self.chats_cache[chat_name] = self._process_messages(messages, names, title)

    def _get_paths(self, chat_id: str) -> list[Path]:
        """Gets paths to the inbox folders with desired chat.

        :param chat_id: chat ID of the desired chat
        :return: list of Path objects to the inbox folders
        """
        paths = []

        for folder in self.folders:
            path_name = f"{folder}/inbox/{chat_id}"
            if os.path.isdir(path_name):
                paths.append(Path(path_name))

        return paths

    def _get_jsons_title_names(self, chat_paths) -> tuple[list[str], str, list[str]]:
        """Gets the json(s) with messages for a particular chat

        :param chat_paths: list of paths to the inbox folders of the chat
        :return: jsons - JSON files with the messages,
                 title - name of the conversation,
                 names - names of conversation participants
        """
        jsons = []
        for ch in chat_paths:
            for file in os.listdir(ch):
                if file.startswith("message") and file.endswith(".json"):
                    jsons.append(ch / file)
                if file == "message_1.json":
                    with open(ch / file) as last:
                        data = json.load(last)
                        title, names = self._get_title_and_names(data)
        if not jsons:
            raise Exception("NO JSON FILES IN THIS CHAT")
        return jsons, title, names

    def _get_messages(self, jsons: "list[str]") -> list:
        """Gets the messages for a conversation.

        :param jsons: JSON files containing the messages
        :return: list of messages
        """
        messages = []
        for j in jsons:
            with open(j, "r") as data:
                data = json.load(data)
                messages.extend(data["messages"])
        messages = sorted(messages, key=lambda k: k["timestamp_ms"])
        self._decode_messages(messages)
        return messages

    def _get_title_and_names(self, chat: dict) -> tuple[str, list[str]]:
        """Gets names of the participants in the chat and the title of the chat."""
        participants = []
        for i in chat["participants"]:
            participants.append(self._decode(i["name"]))
        if len(participants) == 1:
            participants.append(participants[0])

        title = self._decode(chat["title"])
        return title, participants

    def _process_messages(self, messages: list, names, title) -> FacebookMessengerChat:
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
        reactions = {"total": 0, "types": {}, "gave": {}, "got": {}}
        emojis = {"total": 0, "types": {}, "sent": {}}
        days = self._days_list(messages)
        months = {}
        years = {}
        weekdays = {}
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
                        if any(char in emoji.EMOJI_DATA for char in c):
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

        return FacebookMessengerChat(
            messages, basic_stats, reactions, emojis, times, people, from_day, to_day, names, title
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
                name = str(chat_id).split("_")[0].lower()

                if name not in self.chat_ids:
                    self.chat_ids[name] = [str(chat_id).lower()]
                else:
                    previous_id = self.chat_ids[name][0]
                    if chat_id != previous_id:
                        self.chat_ids[name].append(str(chat_id).lower())

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
            jsons[chat_id], _, names[chat_id] = self._get_jsons_title_names(chat_paths[chat_id])
            lengths[chat_id] = [(len(jsons[chat_id]) - 1) * 10000, len(jsons[chat_id]) * 10000]
            print(
                f"{chat_ids.index(chat_id)+1}) with {names[chat_id]} and {lengths[chat_id][0]}-{lengths[chat_id][1]} messages"
            )
