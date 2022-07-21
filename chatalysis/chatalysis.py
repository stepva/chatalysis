# Standard library imports
import webbrowser
import pathlib
import io
import sys
import threading
from pprint import pprint
# Application imports
from __init__ import version
from analysis import raw, chatStats, reactionStats, emojiStats, timeStats, firstMsg
from infographic import mrHtml
from utility import getPaths, getJsons, getMsgs, home

# Chatalyses the chat and produces an HTML output
def htmllyse(chats, folders: list[str]):
    chat_paths = getPaths(chats, folders)
    jsons, title, names = getJsons(chat_paths)
    messages = getMsgs(jsons)
    basicStats, reactions, emojis, times, _, fromDay, toDay, names = raw(messages, names)

    source = mrHtml(version, names, basicStats, fromDay, toDay, times, emojis, reactions, title)

    with io.open(f"{home}/../output/{title}.html", "w", encoding="utf-8") as data:
        data.write(source)

    if sys.platform == 'darwin':
        wb = webbrowser.get("safari")
    else:
        wb = webbrowser.get()
    wb.open(f"file:///{home}/../output/{title}.html")

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
