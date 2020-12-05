# Standard library imports
import argparse
import os
from pprint import pprint
# Application imports
from __init__ import version
from analysis import *
from output import mrHtml
from utility import *
from interface import *


def main(argv=None):
    home = os.getcwd()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '-version', '--version', help='Version', action='version', version=version)
    parser.add_argument("-t", "--terminal", action="store_true")
    args = parser.parse_args(argv)
    
    if args.terminal:
        name = input()
        terminalyse(name, home)
    else:    
        header()
        tops=0
        while True:
            inp = getInput()

            if inp == "top":
                if tops==0:
                    tops=topTen(home)
                pprint(tops, indent=2, sort_dicts=False)
            elif inp == "help":
                print("soon")
            elif inp == "exit":
                break
            else:
                chatalyse(inp, home)

            if inp == "exit":
                break

            print("\nDone!\n")
            #rework this again thingy:
            again = input("Again? Type \"no\" to close this, hit enter to go again: ")
            if again == "no":
                break

    
if __name__ == "__main__":
    main()
