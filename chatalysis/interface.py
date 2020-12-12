# Standard library imports
import webbrowser
import pathlib
import io
import platform
import threading
from pprint import pprint
# Application imports
from __init__ import version
from analysis import *
from infographic import mrHtml
from utility import *

# Interface header
def header():
    print("************************************")
    print(f"Welcome to Chatalysis {version}!\n")
    print("What do you want to do?\n")

# Main interface, asks for an input
def getInput():
    print(
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
    with io.open(f"{home}/../output/{name}.html", "w", encoding="utf-8") as data:
        data.write(final)
    if platform.system() == "Windows":
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        def x(): return webbrowser.get(chrome_path).open_new(f"file:///{home}/../output/{name}.html")
        t = threading.Thread(target=x)
        t.start()
        print("You can find it in the output folder and open it in your favourite browser!")
    elif platform.system() == "Darwin":
        webbrowser.open(f"file:///{home}/../output/{name}.html")
    else:
        print("Could’t open the file, but you can find it in the output folder and open it in your favourite browser!")


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
