import argparse
import sys

from chatalysis.__init__ import __version__
from chatalysis.program.program import Program


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "-version", help="Version info", action="version", version=__version__)

    subparses = parser.add_subparsers()
    subparses.add_parser("cli", help="Use CLI instead of GUI")

    p = Program()

    if "cli" in sys.argv:
        p.run(cli=True)
    else:
        p.run()


if __name__ == "__main__":
    main()
