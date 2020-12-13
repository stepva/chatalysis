# Standard library imports
import argparse
import os
import pathlib
from pprint import pprint

# Application imports
from __init__ import version
from infographic import mrHtml
from utility import identifyChats
from chatalysis import printlyse, htmllyse


def main(argv=None):
    chats = identifyChats()

    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '-version', '--version', help='Version', action='version', version=version)
    parser.add_argument('chat', nargs='?', type=str, choices=chats.keys())
    args = parser.parse_args(argv)

    if args.chat:
        printlyse(chats[args.chat])
        exit()
    
    tops = None
    i = ''

    print("************************************")
    print(f"Welcome to Chatalysis {version}!\n")
    print("What do you want to do?\n")
    print("To see your Top 10 chats, just type \"top\"\n", \
            "To chatalyse a specific conversation, just say which one - \"namesurname\"\n", \
            "If you need help, read the README\n", \
            "To exit, just type \"exit\":\n")

    while i != 'exit':
        i = input()
        chat = chats.get(i)

        if i == "top":
            print("Loading...\n")
            if not tops:
                tops = topTen()

            pprint(tops, indent=2, sort_dicts=False)

        elif chat is not None:
            print("Loading...")
            htmllyse(chat)

        elif i != 'exit':
            print(f'No chats named {i}. Try again.')


    
if __name__ == "__main__":
    main()
