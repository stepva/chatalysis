# Standard library imports
import os
import json
import pathlib

# Third party imports
from bs4 import BeautifulSoup

home = pathlib.Path(__file__).parent.absolute()


def identifyChats(folders: "list[str]"):
    """Gets list of all conversations and their ID"""
    chats = {}

    for folder in folders:
        for chat_id in os.listdir(f"{folder}/inbox"):
            name = chat_id.split("_")[0].lower()

            if name not in chats:
                chats[name] = [chat_id.lower()]
            else:
                previous_id = chats[name][0]
                if chat_id != previous_id:
                    chats[name].append(chat_id.lower())
    return chats


def getMessageFolders(path: str) -> "list[str]":
    """Gets the messages folders"""
    folders = []

    for d in os.listdir(path):
        if d.startswith("messages") and os.path.isdir(f"{path}/{d}"):
            folders.append(f"{path}/{d}")

    if len(folders) == 0:
        raise Exception(
            'Looks like there is no "messages" folder here. Make sure to add the "messages" folder downloaded from Facebook as desribed in the README :)'
        )

    return folders


def checkMedia(folders: "list[str]"):
    """Checks if all media types are included, as for some users Facebook doesn’t include files or videos"""
    media = {"photos": 0, "videos": 0, "files": 0, "gifs": 0, "audio": 0}

    for folder in folders:
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
            f"These media types are not included in your messages for some reason: {no_media_str}. I can’t do anything about it.\n"
        )


def getPaths(chat_ids, folders: "list[str]"):
    """Gets path(s) to the desired chat(s)"""
    chat_paths = []

    if len(chat_ids) == 1:
        i = 0
    else:
        print(f"There are {len(chat_ids)} different chats with this name:")
        multipleChats(chat_ids, folders)
        i = int(input("Which one do you want? ")) - 1

    for folder in folders:
        for chat in os.listdir(f"{folder}/inbox"):
            if chat.lower() == chat_ids[i]:
                chat_paths.append(f"{folder}/inbox/{chat}")
    return chat_paths


def multipleChats(chat_ids, folders):
    """Gets information about chats with the same name"""
    chat_paths = {}
    jsons = {}
    names = {}
    lengths = {}

    for chat_id in chat_ids:
        chat_paths[chat_id] = getPaths([chat_id], folders)
        jsons[chat_id], _, names[chat_id] = getJsons(chat_paths[chat_id])
        lengths[chat_id] = [
            (len(jsons[chat_id]) - 1) * 10000,
            len(jsons[chat_id]) * 10000,
        ]
        print(
            f"{chat_ids.index(chat_id)+1}) with {names[chat_id]} and {lengths[chat_id][0]}-{lengths[chat_id][1]} messages"
        )


def getJsons(chat_paths):
    """Gets the json(s) with desired messages"""
    jsons = []
    for ch in chat_paths:
        for file in os.listdir(ch):
            if file.startswith("message") and file.endswith(".json"):
                jsons.append(f"{ch}/{file}")
            if file == "message_1.json":
                with open(f"{ch}/{file}") as last:
                    data = json.load(last)
                    title = decode(data["title"])
                    names = getNames(data)
    if not jsons:
        raise Exception("NO JSON FILES IN THIS CHAT")
    return (jsons, title, names)


def getMsgs(jsons):
    """Gets the desired messages"""
    messages = []
    for j in jsons:
        with open(j) as data:
            data = json.load(data)
            messages.extend(data["messages"])
    messages = sorted(messages, key=lambda k: k["timestamp_ms"])
    decodeMsgs(messages)
    return messages


def getNames(data):
    """Gets names of the participants in the chat."""
    ns = []
    for i in data["participants"]:
        ns.append(i["name"].encode("iso-8859-1").decode("utf-8"))
    if len(ns) == 1:
        ns.append(ns[0])
    return ns


def decode(word: str) -> str:
    """Decode a string from the Facebook encoding."""
    return word.encode("iso-8859-1").decode("utf-8")


def decodeMsgs(messages):
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


def get_messages_from_html(file_path: str) -> int:
    """Find the number of total messages from a previously generated HTML file"""
    f = open(file_path, "r", encoding="utf-8")
    soup = BeautifulSoup(f, features="html.parser")
    field = soup.find("p", {"id": "total messages"})
    if field:
        messages = int(field.text.replace(" ", "").replace(",", ""))
    else:
        messages = 0
    return messages
