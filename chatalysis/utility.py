# Standard library imports
import os
from pathlib import Path
import webbrowser
import sys

# Third party imports
from bs4 import BeautifulSoup

home = Path(__file__).parent.absolute()


def get_messages_from_html(file_path: str) -> int:
    """Find the number of total messages from a previously generated HTML file"""
    f = open(file_path, "r", encoding="utf-8")
    soup = BeautifulSoup(f, features="html.parser")
    field = soup.find("p", {"id": "total messages"})
    if field:
        messages = int(
            # remove number formatting
            field.text.replace(" ", "")
            .replace("\u202f", "")  # \u202f is a no-break space
            .replace(",", "")
        )
    else:
        messages = 0
    return messages


def html_spaces(n):
    """Splits number by thousands with a space"""
    return "{0:n}".format(n) if n != 1 else n


def open_html(path: str):
    """Opens the html file in a browser"""
    if sys.platform == "darwin":
        wb = webbrowser.get("safari")
        path_to_open = f"file://{path}"
    else:
        wb = webbrowser.get()
        path_to_open = path

    wb.open(path_to_open)


def check_if_create_new(title: str, messages: dict):
    """Checks if the html file of a chat's title exists and compares it with the chat's messages"""
    file_path = home / ".." / "output" / f"{title}.html"

    if os.path.exists(file_path):
        html_messages = get_messages_from_html(file_path)
        if len(messages) == html_messages:
            open_html(file_path)
            return False

    return True


def hours_list() -> "dict[int, int]":
    """Creates a dictionary of hours in a day

    :return: dictionary of hours
    """
    hours = {}
    for i in range(24):
        hours[i] = 0
    return hours


def get_file_path(title: str):
    """Returns a file_path of the chosen chat title"""
    return home / ".." / "output" / f"{title}.html"
