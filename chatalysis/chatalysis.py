# Standard library imports
import webbrowser
import io
import sys
import os
from pprint import pprint
# Application imports
from __init__ import __version__
from analysis import raw, chatStats, reactionStats, emojiStats, timeStats, firstMsg
from infographic import mrHtml
from utility import getPaths, getJsons, getMsgs, home

def htmllyse(chats: "list[str]", folders: "list[str]"):
    """Analyzes the chat and creates HTML output file with stat visualization

    :param chats: list of the chats to analyze
    :param folders: list of folders containing the messages and other data (pictures etc.)
    """
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

def printlyse(chats: "list[str]"):
    """Analyzes the chat and prints the stats to terminal

    :param chats: list of the chats to analyze
    """
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
