# Standard library imports
import webbrowser
import pathlib
from pprint import pprint
# Application imports
from __init__ import version
from analysis import *
from infographic import mrHtml
from utility import *

home = pathlib.Path(__file__).parent.absolute()

# Interface header
def header():
    print("************************************")
    print(f"Welcome to Chatalysis {version}!\n")

# Main interface, asks for an input
def getInput():
    print(
        "\nWhat do you want to do?\n"
        "To see your Top 10 chats, just type \"top\"\n"
        "To chatalyse a specific conversation, just say which one - \"namesurname\"\n"
        "If you need help, read the README\n"
        "To exit, just type \"exit\":")
    inp = input()
    print()
    if inp != "exit":
        print("Loading...\n")
    return inp

# Chatalyses the chat and produces an HTML output
def chatalyse(name):
    chats = getChats(name)
    jsons, title, names = getJsons(chats)
    messages = getMsgs(jsons)
    basicStats, reactions, emojis, times, people, fromDay, toDay, names = raw(messages, names)
    final = mrHtml(version, names, basicStats, fromDay, toDay, times, emojis, reactions, title)
    with open(f"{home}/../output/{name}.html", "w") as data:
        data.write(final)
    webbrowser.open(f"file:///{home}/../output/{name}.html")

# Chatalyses the chat and prints it to terminal
def terminalyse(name):
    chats = getChats(name)
    jsons, title, names = getJsons(chats)
    messages = getMsgs(jsons)
    basicStats, reactions, emojis, times, people, fromDay, toDay, names = raw(messages, names)

    print(f"Chat: {title}, from {fromDay} to {toDay}")
    pprint(chatStats(basicStats, names), indent=2, sort_dicts=True)
    pprint(reactionStats(reactions, names, people), indent=2, sort_dicts=False)
    pprint(emojiStats(emojis, names, people), indent=2, sort_dicts=False)
    pprint(timeStats(times), indent=2, sort_dicts=False)
    pprint(firstMsg(messages), indent=2, sort_dicts=False)
