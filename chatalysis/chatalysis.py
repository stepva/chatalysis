# Standard library imports
import webbrowser
import pathlib
import io
import sys
import os
import threading
from pprint import pprint
# Application imports
from __init__ import __version__
from analysis import raw, chatStats, reactionStats, emojiStats, timeStats, firstMsg
from infographic import mrHtml
from utility import getPaths, getJsons, getMsgs, home

# Chatalyses the chat and produces an HTML output
def htmllyse(chats, folders: "list[str]"):
    chat_paths = getPaths(chats, folders)
    jsons, title, names = getJsons(chat_paths)

    if sys.platform == 'darwin':
        wb = webbrowser.get("safari")
    else:
        wb = webbrowser.get()

    file = f"{home}/../output/{title}.html"

    if os.path.exists(file):
        wb.open(file)
        return

    messages = getMsgs(jsons)
    basicStats, reactions, emojis, times, _, fromDay, toDay, names = raw(messages, names)

    source = mrHtml(__version__, names, basicStats, fromDay, toDay, times, emojis, reactions, title)

    with io.open(file, "w", encoding="utf-8") as data:
        data.write(source)

    wb.open(file)

# Chatalyses the chat and prints it to terminal
def printlyse(chats):
    chat_paths = getPaths(chats)
    jsons, title, names = getJsons(chat_paths)
    messages = getMsgs(jsons)
    basicStats, reactions, emojis, times, people, fromDay, toDay, names = raw(messages, names)

    print(f"Chat: {title}, from {fromDay} to {toDay}")
    pprint(chatStats(basicStats, names), indent=2, sort_dicts=True)
    pprint(reactionStats(reactions, names, people), indent=2, sort_dicts=False)
    pprint(emojiStats(emojis, names, people), indent=2, sort_dicts=False)
    pprint(timeStats(times), indent=2, sort_dicts=False)
    pprint(firstMsg(messages), indent=2, sort_dicts=False)
