import os
import json
import io
from datetime import datetime, date, timedelta
from pprint import pprint


from pathlib import Path
from analyzer import Analyzer
from chat import Chat
from utility import open_html
from utility import get_file_path
from utility import check_if_create_new, hours_list
from message_source import MessageSource

import regex
import emoji


class FacebookMessenger(MessageSource):
    def __init__(self, path: str):
        MessageSource.__init__(self, path)
        self.folders = self.get_message_folders()
        self.chats = self.get_all_chats()
        self._check_media()
        self.path = path

    def get_all_chats(self):
        """Gets list of all conversations and their ID"""
        chats = {}

        for folder in self.folders:
            for chat_id in os.listdir(Path(folder) / "inbox"):
                name = chat_id.split("_")[0].lower()

                if name not in chats:
                    chats[name] = [chat_id.lower()]
                else:
                    previous_id = chats[name][0]
                    if chat_id != previous_id:
                        chats[name].append(chat_id.lower())
        return chats

    def get_chat(self, chat_name: str):
        return self.chats.get(chat_name)

    def to_html(self, chat: "list[str]"):
        chat_paths = self._get_paths(chat)
        jsons, title, names = self._get_jsons_title_names(chat_paths)
        messages = self._get_messages(jsons)

        create_new = check_if_create_new(title, messages)
        if not create_new:
            return

        CHAT = self.process_messages(messages, names, title)

        ANALYZER = Analyzer(CHAT)

        source = ANALYZER.mrHtml()

        file_path = get_file_path(title)

        with io.open(file_path, "w", encoding="utf-8") as data:
            data.write(source)

        open_html(file_path)
        return

    def to_cli(self, chat: "list[str]"):
        """Analyzes the chat and prints the stats to terminal

        :param chats: list of the chats to analyze
        """
        chat_paths = self._get_paths(chat)
        jsons, title, names = self._get_jsons_title_names(chat_paths)
        messages = self._get_messages(jsons)

        CHAT = self.process_messages(messages, names, title)

        ANALYZER = Analyzer(CHAT)

        print(f"Chat: {title}, from {CHAT.from_day} to {CHAT.to_day}")
        pprint(ANALYZER.chat_stats(CHAT.basic_stats, names), indent=2, sort_dicts=True)
        pprint(
            ANALYZER.reaction_stats(CHAT.reactions, names, CHAT.people),
            indent=2,
            sort_dicts=False,
        )
        pprint(
            ANALYZER.emoji_stats(CHAT.emojis, names, CHAT.people),
            indent=2,
            sort_dicts=False,
        )
        pprint(ANALYZER.time_stats(CHAT.times), indent=2, sort_dicts=False)
        pprint(self.first_message(messages), indent=2, sort_dicts=False)

        return

    def get_message_folders(self) -> "list[str]":
        """Get folders containing the messages"""
        folders = []

        for d in os.listdir(self.data_dir_path):
            if d.startswith("messages") and os.path.isdir(f"{self.data_dir_path}/{d}"):
                folders.append(f"{self.data_dir_path}/{d}")

        if not folders:
            raise Exception(
                """Looks like there is no "messages" folder here. Make sure to add the "messages" folder downloaded 
                from Facebook as desribed in the README :)"""
            )

        return folders

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
                f"""These media types are not included in your messages for some reason: {no_media_str}. 
                I can’t do anything about it.\n"""
            )

    def _get_paths(self, chat_ids: "list[str]"):
        """Gets path(s) to the desired chat(s)"""
        chat_paths = []

        if len(chat_ids) == 1:
            i = 0
        else:
            print(f"There are {len(chat_ids)} different chats with this name:")
            self._multiple_chats(chat_ids)
            i = int(input("Which one do you want? ")) - 1

        for folder in self.folders:
            for chat in os.listdir(Path(folder) / "inbox"):
                if chat.lower() == chat_ids[i]:
                    chat_paths.append(Path(folder) / "inbox" / Path(chat))
        return chat_paths

    def _multiple_chats(self, chat_ids: "list[str]"):
        """Gets information about chats with the same name"""
        chat_paths = {}
        jsons = {}
        names = {}
        lengths = {}

        for chat_id in chat_ids:
            chat_paths[chat_id] = self._get_paths([chat_id], self.folders)
            jsons[chat_id], _, names[chat_id] = self._get_jsons(chat_paths[chat_id])
            lengths[chat_id] = [
                (len(jsons[chat_id]) - 1) * 10000,
                len(jsons[chat_id]) * 10000,
            ]
            print(
                f"{chat_ids.index(chat_id)+1}) with {names[chat_id]} and {lengths[chat_id][0]}-{lengths[chat_id][1]} messages"
            )

    def _get_jsons_title_names(self, chat_paths: "list[str]"):
        """Gets the json(s) with desired messages"""
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
        return (jsons, title, names)

    def _get_messages(self, jsons: "list[str]"):
        """Gets the desired messages"""
        messages = []
        for j in jsons:
            with open(j) as data:
                data = json.load(data)
                messages.extend(data["messages"])
        messages = sorted(messages, key=lambda k: k["timestamp_ms"])
        self._decode_messages(messages)
        return messages

    def _get_title_and_names(self, chat: dict):
        """Gets names of the participants in the chat."""
        ns = []
        for i in chat["participants"]:
            ns.append(i["name"].encode("iso-8859-1").decode("utf-8"))
        if len(ns) == 1:
            ns.append(ns[0])

        title = self._decode(chat["title"])
        return (title, ns)

    def _decode(self, word: str) -> str:
        """Decode a string from the Facebook encoding."""
        return word.encode("iso-8859-1").decode("utf-8")

    def _decode_messages(self, messages: dict):
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

    def process_messages(self, messages: list, names: "list[str]", title: str):
        fromDay = date.fromtimestamp(messages[0]["timestamp_ms"] // 1000)
        toDay = date.fromtimestamp(messages[-1]["timestamp_ms"] // 1000)
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
        hours = hours_list()

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
                    reactions["types"][reaction] = 1 + reactions["types"].get(
                        reaction, 0
                    )
                    if name in names:
                        reactions["got"][name]["total"] += 1
                        reactions["got"][name][reaction] = 1 + reactions["got"][
                            name
                        ].get(reaction, 0)
                        if r["actor"] in names:
                            reactions["gave"][r["actor"]]["total"] += 1
                            reactions["gave"][r["actor"]][reaction] = 1 + reactions[
                                "gave"
                            ][r["actor"]].get(reaction, 0)

        basicStats = (people, photos, gifs, stickers, videos, audios, files)
        times = (hours, days, weekdays, months, years)

        return Chat(
            basicStats, reactions, emojis, times, people, fromDay, toDay, names, title
        )

    def _days_list(self, messages: list) -> "dict[str, int]":
        """Prepares a dictionary with all days from the first message up to the last one

        :param messages: list of messages in the conversation
        :return: dictionary of days
        """
        fromDay = date.fromtimestamp(messages[0]["timestamp_ms"] // 1000)
        toDay = date.fromtimestamp(messages[-1]["timestamp_ms"] // 1000)
        delta = toDay - fromDay
        days = {}
        for i in range(delta.days + 1):
            day = fromDay + timedelta(days=i)
            days[str(day)] = 0
        return days

    def first_message(self, messages: list) -> dict:
        """Returns the first conversation ever

        :param messages: list of the messages in a conversation
        :return: dictionary with the first message
        """
        author = messages[0]["sender_name"]
        texts = {}
        i = 0
        while True:
            if messages[i]["sender_name"] == author:
                texts[messages[i]["sender_name"]] = messages[i]["content"]
                i += 1
            else:
                texts[messages[i]["sender_name"]] = messages[i]["content"]
                break
        return texts

    def top_ten(self) -> "tuple[dict[str, int], dict[str, int]]":
        """Goes through conversations and returns the top 10 individual chats
        and top 5 group chats based on messages number.

        :param path: path to a directory with all the messages
        :return: dictionary of top 10 individual conversations & top 5 group chats
                with the structure {conversation name: number of messages}
        """
        chats = {}
        groups = {}
        inboxes = [
            f"{self.path}/{m}/inbox/"
            for m in os.listdir(self.path)
            if m.startswith("messages")
        ]
        names = [i + n for i in inboxes for n in os.listdir(i) if os.path.isdir(i + n)]
        ts = 0

        for n in names:
            for file in os.listdir(n):
                if file.startswith("message") and file.endswith(".json"):
                    with open(n + "/" + file) as data:
                        data = json.load(data)

                        # get the "real" name of the individual conversation (as opposed to the "condensed"
                        # format in the folder name (represented here by the variable "m"))
                        conversationName = (
                            data["title"].encode("iso-8859-1").decode("utf-8")
                        )

                        if data["thread_type"] == "Regular":
                            chats[conversationName] = len(data["messages"]) + chats.get(
                                conversationName, 0
                            )
                        elif data["thread_type"] == "RegularGroup":
                            groups[conversationName] = len(
                                data["messages"]
                            ) + groups.get(conversationName, 0)

                        if data["messages"][0]["timestamp_ms"] > ts:
                            ts = data["messages"][0]["timestamp_ms"]

        top_individual = dict(
            sorted(chats.items(), key=lambda item: item[1], reverse=True)[0:10]
        )
        top_group = dict(
            sorted(groups.items(), key=lambda item: item[1], reverse=True)[0:5]
        )
        return top_individual, top_group
