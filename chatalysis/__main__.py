
# Standard library imports
import json
import argparse
import os
from datetime import datetime, date
from pprint import pprint
# Third party imports
import emoji
import regex
import matplotlib.pyplot as plt
# Application imports
from __init__ import version
from analysis import *
from output import mrHtml


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '-version', '--version', help='Version', action='version', version=version)
    parser.add_argument("chat", help="Chat Name")
    parser.add_argument("-t", "--terminal", action="store_true")
    parser.add_argument("-o", "--output", action="store_true")
    args = parser.parse_args(argv)
    """
    pprint(topTen(), indent=2, sort_dicts=False)
    """
    home = os.getcwd()
    chats = []
    for d in os.listdir(home):
        if d.startswith("messages") and os.path.isdir(f"{home}/{d}"):
            for f in os.listdir(d + "/inbox"):
                if f.startswith(args.chat + "_"):
                    chats.append(f"{d}/inbox/{f}")

    if not chats:
        raise Exception("NO CHATS NAMED " + args.chat)

    jsons = []
    for ch in chats:
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

    messages = []
    for j in jsons:    
        with open(j) as data:
            data = json.load(data)
            messages.extend(data["messages"])
    messages = sorted(messages, key=lambda k: k["timestamp_ms"])
    decodeMsgs(messages)

    basicStats, reactions, emojis, times, people, fromDay, toDay, names = raw(messages, names)
    daysList(messages)
    
    if args.terminal:
        header(title, messages)
        pprint(chatStats(basicStats, names), indent=2, sort_dicts=True)
        pprint(reactionStats(reactions, names, people), indent=2, sort_dicts=False)
        pprint(emojiStats(emojis, names, people), indent=2, sort_dicts=False)
        pprint(timeStats(times), indent=2, sort_dicts=False)
        pprint(firstMsg(messages), indent=2, sort_dicts=False)

    if args.output:
        final = mrHtml(version, names, basicStats, fromDay, toDay, times, emojis, reactions, title)
        with open(f"output/{args.chat}.html", "w") as data:
            data.write(final)
    


if __name__ == "__main__":
    main()
