import abc
import json
import os
import regex
from datetime import date, timedelta
from pathlib import Path
from statistics import mode

import emoji

from utils.const import EMOJIS_REGEX, EMOJIS_DICT
from chats.stats import StatsType, FacebookStats
from sources.message_source import MessageSource, NoMessageFilesError
from utils.utility import list_folder

chat_id_str = str  # alias for str that denotes a unique chat ID (for example: "johnsmith_djnas32owkldm")


class FacebookSource(MessageSource):
    """Abstract parent class for Facebook Messenger and Instagram. The message format for both
    is almost identical (with only minor differences), so only the _process_messages method is abstract.
    """

    def __init__(self, path: str):
        MessageSource.__init__(self, path)
        self.folders: list[Path] = []
        self.chat_ids: set[str] = set()  # list of all conversations identified by their chat ID

        # Intermediate cache of the extracted but not yet processed messages. The values stored are tuples of
        # messages, names of the chat participants, chat title and chat type. Once the messages have been processed,
        # they are removed from this cache as they can be accessed via the Chat object.
        self.messages_cache: dict[chat_id_str, tuple[list, list, str, StatsType]] = {}

        # cache of Stats objects
        self.chats_cache: dict[chat_id_str, FacebookStats] = {}

        self._load_message_folders()
        self._load_all_chats()

    # region Public API

    def get_chat(self, chat_id: str) -> FacebookStats:
        if chat_id not in self.chats_cache:
            self._compile_chat_data(chat_id)
        return self.chats_cache[chat_id]

    def personal_stats(self) -> FacebookStats:
        messages = []
        participants = []  # list of participants from all conversations

        for chat_id in self.chat_ids:
            if chat_id in self.chats_cache:
                messages.extend(self.chats_cache[chat_id].messages)
                participants.extend(self.chats_cache[chat_id].participants)
            elif chat_id in self.messages_cache:
                messages.extend(self.messages_cache[chat_id][0])
                participants.extend(self.messages_cache[chat_id][1])
            else:
                # extract data for the chat and cache it
                self.messages_cache[chat_id] = self._prepare_chat_data(chat_id)
                messages.extend(self.messages_cache[chat_id][0])
                participants.extend(self.messages_cache[chat_id][1])

        # find the user's name (the one that appears in all conversations)
        name = mode(participants)

        messages = [m for m in messages if m["sender_name"] == name]
        messages = sorted(messages, key=lambda k: k["timestamp_ms"])
        return self._process_messages(messages, [name], "Personal stats", StatsType.PERSONAL)

    def top_ten(self):
        chats = {}
        groups = {}

        for chat_id in self.chat_ids:
            if chat_id in self.chats_cache:
                title = self.chats_cache[chat_id].title
                chat_type = self.chats_cache[chat_id].stats_type
                messages = self.chats_cache[chat_id].messages
            elif chat_id in self.messages_cache:
                messages, _, title, chat_type = self.messages_cache[chat_id]
            else:
                # extract data for the chat and cache it
                messages, participants, title, chat_type = self._prepare_chat_data(chat_id)
                self.messages_cache[chat_id] = messages, participants, title, chat_type

            # remove emoji because it ruins the aligning of the output text
            title = emoji.replace_emoji(title, "")

            if chat_type == StatsType.REGULAR:
                chats[title] = len(messages)
            elif chat_type == StatsType.GROUP:
                groups[title] = len(messages)

        top_individual = sorted(chats.items(), key=lambda item: item[1], reverse=True)[0:10]
        top_group = sorted(groups.items(), key=lambda item: item[1], reverse=True)[0:5]
        return top_individual, top_group

    def conversation_size(self, chat: str) -> int:
        messages, _, _, _ = self._get_messages(chat)
        return len(messages)

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

    def _prepare_chat_data(self, chat_id: chat_id_str) -> tuple[list, list, str, StatsType]:
        """Extracts the chat data and decodes the messages

        :param chat_id: ID of the chat to process
        :return: messages - list of messages
                 title - name of the conversation,
                 participants - names of conversation participants
                 chat_type - type of chat (regular chat, group chat)
        """
        messages, participants, title, chat_type = self._get_messages(chat_id)
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
            path_name = f"{folder}/{chat_id}"
            if os.path.isdir(path_name):
                paths.append(Path(path_name))

        return paths

    def _get_jsons(self, chat_id: str) -> list[Path]:
        """Gets the json(s) with messages for a particular chat

        :param chat_id: chat ID of the desired chat
        :return: list of JSON files with the messages
        """
        paths = self._get_paths(chat_id)
        jsons = []

        for ch in paths:
            for file in list_folder(ch):
                if file.startswith("message") and file.endswith(".json"):
                    jsons.append(ch / file)
        if not jsons:
            raise NoMessageFilesError(f"{chat_id} - no JSON files in this chat")

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

    def _get_messages(self, chat_id: chat_id_str) -> tuple[list[dict], list[str], str, StatsType]:
        """Gets the chat data (messages, names of the participants, chat title and chat type)

        :param chat_id: ID of the chat to process
        :return: messages - list of messages
                 title - name of the conversation,
                 participants - names of conversation participants
                 chat_type - type of chat (regular chat, group chat)
        """
        jsons = self._get_jsons(chat_id)
        messages = []

        first = True
        for json_file in jsons:
            with open(json_file, "r") as data_file:
                data = json.load(data_file)
                messages.extend(data["messages"])

                if first:
                    # get title, participants and chat type, which are the same across all JSONs
                    title = self._decode(data["title"])
                    participants = self._get_participants(data)

                    if data["thread_type"] == "RegularGroup":
                        chat_type = StatsType.GROUP
                    else:
                        chat_type = StatsType.REGULAR

                    first = False

        return messages, participants, title, chat_type

    @abc.abstractmethod
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

    def _process_reactions(self, message: dict, name: str, participants: list[str], reactions: dict):
        """Extracts reactions from a message and expands the reaction stats.

        :param message: message to analyze
        :param name: name of the message author
        :param participants: list of the chat participants
        :param reactions: dictionary with reaction stats
        :return: expanded reactions dict
        """
        for r in message["reactions"]:
            if r["reaction"] == self._decode("\u00e2\u009d\u00a4"):
                reaction = "❤️"
            else:
                reaction = r["reaction"]
            reactions["total"] += 1
            reactions["types"][reaction] = 1 + reactions["types"].get(reaction, 0)
            if name in participants:
                reactions["got"][name]["total"] += 1
                reactions["got"][name][reaction] = 1 + reactions["got"][name].get(reaction, 0)
                if r["actor"] in participants:
                    reactions["gave"][r["actor"]]["total"] += 1
                    reactions["gave"][r["actor"]][reaction] = 1 + reactions["gave"][r["actor"]].get(reaction, 0)

        return reactions

    @staticmethod
    def _extract_emojis(message: dict, emojis: dict) -> dict:
        """Extracts both actual Unicode emojis and text emojis (such as ":D") from a message.

        :param message: message to analyze
        :param emojis: emojis dict to which the extracted emoji should be added
        :return: expanded emojis dict
        """
        # don't touch this, hours of academic research have been spent on this function and I don't want to deal with it again any time soon

        name = message["sender_name"]
        data = regex.findall(r"\X", regex.sub(r"[a-z]+", "", message["content"]))

        text_emoji = regex.search(EMOJIS_REGEX, message["content"])
        if text_emoji:
            data.extend([EMOJIS_DICT[e] for e in text_emoji.groups()])

        for c in data:
            if c in emoji.EMOJI_DATA:
                emojis["total"] += 1
                emojis["types"][c] = 1 + emojis["types"].get(c, 0)
                emojis["sent"][name]["total"] += 1
                emojis["sent"][name][c] = 1 + emojis["sent"][name].get(c, 0)

        return emojis

    # endregion

    # region Data source processing

    def _load_message_folders(self):
        """Load folders containing the messages"""
        self.folders = [Path(root, d) for root, dirs, _ in os.walk(self._data_dir_path) for d in dirs if d == "inbox"]
        if not self.folders:
            raise NoMessageFilesError('Looks like there is no "inbox" folder with the messages here.')

    def _load_all_chats(self):
        """Load all chats from the source"""
        for folder in self.folders:
            for chat_id in list_folder(folder):
                if not chat_id.startswith("._"):
                    self.chat_ids.add(chat_id)

    # endregion

    # region Facebook-specific utilities

    @staticmethod
    def _decode(word: str) -> str:
        """Decodes a string from the Facebook encoding."""
        return word.encode("iso-8859-1").decode("utf-8")

    @staticmethod
    def _decode_messages(messages: list) -> list:
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
