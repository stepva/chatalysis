import webbrowser
from pprint import pprint
from __init__ import version
from analysis import *
from output import mrHtml
from utility import *

def header():
    print("************************************")
    print(f"Welcome to Chatalysis {version}!\n")

def getInput():
    print("\nTo see your Top 10 chats, just type \"top\"")
    print("To chatalyse a specific conversation, just say which one - \"namesurname\"")
    print("To get help, just type \"help\"")
    print("To exit, just type \"exit\"")
    inp = input("Type: ")
    print()
    if inp != "exit":
        print("Loading...\n")
    return inp

def chatalyse(name, home):
    chats = getChats(home, name)
    jsons, title, names = getJsons(chats)
    messages = getMsgs(jsons)
    basicStats, reactions, emojis, times, people, fromDay, toDay, names = raw(messages, names)
    final = mrHtml(version, names, basicStats, fromDay, toDay, times, emojis, reactions, title)
    with open(f"output/{name}.html", "w") as data:
        data.write(final)
    webbrowser.open(f"file:///{home}/output/{name}.html")

def terminalyse(name, home):
    chats = getChats(home, name)
    jsons, title, names = getJsons(chats)
    messages = getMsgs(jsons)
    basicStats, reactions, emojis, times, people, fromDay, toDay, names = raw(messages, names)

    firstRow(title, messages)
    pprint(chatStats(basicStats, names), indent=2, sort_dicts=True)
    pprint(reactionStats(reactions, names, people), indent=2, sort_dicts=False)
    pprint(emojiStats(emojis, names, people), indent=2, sort_dicts=False)
    pprint(timeStats(times), indent=2, sort_dicts=False)
    pprint(firstMsg(messages), indent=2, sort_dicts=False)
