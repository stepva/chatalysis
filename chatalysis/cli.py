# Standard library imports
import os

# Application imports
from pprint import pprint
from analysis import topTen
from utility import checkMedia, getMessageFolders, identifyChats
from __init__ import __version__
from chatalysis import htmllyse


def cli():
    path = os.getcwd()
    folders = getMessageFolders(path)
    chats = identifyChats(folders)
    if not folders:
        print(
            'Looks like there is no messages folder here. Make sure to add the "messages" folder downloaded from Facebook to the chatalysis parent folder. More info in the README :)'
        )
        exit()

    tops = None
    i = ""

    print("************************************")
    print(f"Welcome to Chatalysis {__version__}!\n")
    checkMedia(folders)
    print(
        """To see your Top 10 chats, just type \"top\"
To chatalyse a specific conversation, just say which one - \"namesurname\"
If you need help, read the README
To exit, just type \"exit\":
        """
    )

    while i != "exit":
        print("What do you want to do?")
        i = input()
        chat = chats.get(i)

        if i == "top":
            print("\nLoading...\n")
            if not tops:
                tops = topTen(path)

            pprint(tops, indent=2, sort_dicts=False)

        elif chat is not None:
            print("\nLoading...\n")
            htmllyse(chat, folders)
            print("Done. You can find it in the output folder!\n")

        elif i != "exit":
            print(f"No chats named {i}. Try again.")

    return
