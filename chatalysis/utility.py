# Standard library imports
import os
import json
import pathlib

home = pathlib.Path(__file__).parent.absolute()


def identifyChats():
    chats = {}
    
    for folder in getMessageFolders():
        for chat_id in os.listdir(f'{folder}/inbox'):
            name = chat_id.split('_')[0].lower()
            
            if name not in chats:
                chats[name] = [chat_id.lower()]
            else:
                previous_id = chats[name][0]
                if chat_id != previous_id:
                    chats[name].append(chat_id.lower())
    return chats

def getMessageFolders():
    folders = []
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

    for d in os.listdir(path):
        if d.startswith("messages") and os.path.isdir(f'{path}/{d}'):
            folders.append(f'{path}/{d}')

    return folders

def getPaths(chat_ids):
    chat_paths = []

    if len(chat_ids) == 1:
        i = 0
    else:
        print(f"There are {len(chat_ids)} different chats with this name:")
        multipleChats(chat_ids)
        i = int(input("Which one do you want? "))-1

    for folder in getMessageFolders():
        for chat in os.listdir(f'{folder}/inbox'):
            if chat.lower() == chat_ids[i]:
                chat_paths.append(f'{folder}/inbox/{chat}')
    return chat_paths

def multipleChats(chat_ids):
    chat_paths = {}
    jsons = {}
    names = {}
    lengths = {}

    for chat_id in chat_ids:
        chat_paths[chat_id] = getPaths([chat_id])
        jsons[chat_id], _, names[chat_id] = getJsons(chat_paths[chat_id])
        lengths[chat_id] = [(len(jsons[chat_id])-1)*10000, len(jsons[chat_id])*10000]
        print(f"{chat_ids.index(chat_id)+1}) with {names[chat_id]} and {lengths[chat_id][0]}-{lengths[chat_id][1]} messages")

# Gets the json(s) with desired messages
def getJsons(chat_paths):
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

# Gets the desired messages
def getMsgs(jsons):
    messages = []
    for j in jsons:
        with open(j) as data:
            data = json.load(data)
            messages.extend(data["messages"])
    messages = sorted(messages, key=lambda k: k["timestamp_ms"])
    decodeMsgs(messages)
    return messages

# Gets names of the participants in the chat
def getNames(data):
    ns = []
    for i in data["participants"]:
        ns.append(i["name"].encode('iso-8859-1').decode('utf-8'))
    if len(ns) == 1:
        ns.append(ns[0])
    return ns

# Decodes a string from the Facebook encoding
def decode(word):
    return word.encode('iso-8859-1').decode('utf-8')

# Decodes all messages from the Facebook encoding
def decodeMsgs(messages):
    for m in messages:
        m["sender_name"] = m["sender_name"].encode('iso-8859-1').decode('utf-8')
        if "content" in m:
            m["content"] = m["content"].encode('iso-8859-1').decode('utf-8')
        if "reactions" in m:
            for r in m["reactions"]:
                r["reaction"] = r["reaction"].encode('iso-8859-1').decode('utf-8')
                r["actor"] = r["actor"].encode('iso-8859-1').decode('utf-8')
    return messages
