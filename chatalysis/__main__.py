# Standard library imports
import argparse
import os
import pathlib
from pprint import pprint
# Application imports
from __init__ import version
from analysis import *
from infographic import mrHtml
from utility import *
from interface import *

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '-version', '--version', help='Version', action='version', version=version)
    parser.add_argument("-t", "--terminal", action="store_true")
    args = parser.parse_args(argv)
    
    if args.terminal:
        name = input()
        terminalyse(name)
    else:    
        header()
        tops=0
        while True:
            inp = getInput()

            if inp == "top":
                if tops==0:
                    tops=topTen()
                pprint(tops, indent=2, sort_dicts=False)
            elif inp == "exit":
                break
            else:
                chatalyse(inp)

            if inp == "exit":
                break

            print("\nDone!\n\nAgain?")

    
if __name__ == "__main__":
    main()
