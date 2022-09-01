# Standard library imports
import os
import json
from pathlib import Path

# Third party imports
from bs4 import BeautifulSoup

home = Path(__file__).parent.absolute()


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
        for chat in os.listdir(Path(folder) / "inbox"):
            if chat.lower() == chat_ids[i]:
                chat_paths.append(Path(folder) / "inbox" / Path(chat))
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
                jsons.append(ch / file)
            if file == "message_1.json":
                with open(ch / file) as last:
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
        messages = int(
            # remove number formatting
            field.text.replace(" ", "")
            .replace("\u202f", "")  # \u202f is a no-break space
            .replace(",", "")
        )
    else:
        messages = 0
    return messages
