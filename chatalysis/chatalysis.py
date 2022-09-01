# Standard library imports
import re
import webbrowser
import io
import sys
import os
from pprint import pprint

# Application imports
from __init__ import __version__
from analysis import raw, chatStats, reactionStats, emojiStats, timeStats, firstMsg
from analyzer import Analyzer
from infographic import mrHtml
from utility import getPaths, getJsons, getMsgs, home, get_messages_from_html
from chat import Chat


def htmllyse(chats: "list[str]", folders: "list[str]"):
    """Analyzes the chat and creates HTML output file with stat visualization

    :param chats: list of the chats to analyze
    :param folders: list of folders containing the messages and other data (pictures etc.)
    """
    chat_paths = getPaths(chats, folders)
    jsons, title, names = getJsons(chat_paths)
    messages = getMsgs(jsons)

    file_path = home / ".." / "output" / f"{title}.html"

    if sys.platform == "darwin":
        path_to_open = f"file://{file_path}"
        wb = webbrowser.get("safari")
    else:
        path_to_open = file_path
        wb = webbrowser.get()

    if os.path.exists(file_path):
        html_messages = get_messages_from_html(file_path)
        if len(messages) == html_messages:
            wb.open(path_to_open)
            return

    basicStats, reactions, emojis, times, people, fromDay, toDay, names = raw(
        messages, names
    )

    CHAT = Chat(
        basicStats, reactions, emojis, times, people, fromDay, toDay, names, title
    )

    ANALYZER = Analyzer(CHAT)

    source = ANALYZER.mrHtml()

    with io.open(file_path, "w", encoding="utf-8") as data:
        data.write(source)

    wb.open(path_to_open)


def printlyse(chats: "list[str]"):
    """Analyzes the chat and prints the stats to terminal

    :param chats: list of the chats to analyze
    """
    chat_paths = getPaths(chats)
    jsons, title, names = getJsons(chat_paths)
    messages = getMsgs(jsons)
    basicStats, reactions, emojis, times, people, fromDay, toDay, names = raw(
        messages, names
    )

    print(f"Chat: {title}, from {fromDay} to {toDay}")
    pprint(chatStats(basicStats, names), indent=2, sort_dicts=True)
    pprint(reactionStats(reactions, names, people), indent=2, sort_dicts=False)
    pprint(emojiStats(emojis, names, people), indent=2, sort_dicts=False)
    pprint(timeStats(times), indent=2, sort_dicts=False)
    pprint(firstMsg(messages), indent=2, sort_dicts=False)
