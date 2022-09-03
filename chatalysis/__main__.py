# Standard library imports
import argparse
import sys

# Application imports
from program import Program
from cli import cli
from __init__ import __version__


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "-version", help="Version info", action="version", version=__version__)

    subparses = parser.add_subparsers()
    parser_cli = subparses.add_parser("cli", help="Use CLI instead of GUI")
    parser_cli.set_defaults(func=cli)

    args = parser.parse_args(argv)

    if "cli" in sys.argv:
        args.func()
    else:
        p = Program()
        p.run()


if __name__ == "__main__":
    main()
