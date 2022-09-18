import os
import sys
import webbrowser
from pathlib import Path

from bs4 import BeautifulSoup

from utils.const import TRANSLATION_TABLE

home = Path(__file__).parent.parent.parent.absolute()


def get_messages_from_html(path: str | Path) -> int:
    """Find the number of total messages from a previously generated HTML file

    :param path: path to the HTML file
    :return: number of messages in the HTML file
    """
    f = open(path, "r", encoding="utf-8")
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


def html_spaces(n: int):
    """Splits number by thousands with a space"""
    return "{0:n}".format(n) if n != 1 else n


def open_html(path: str | Path):
    """Opens the HTML file in a browser

    :param path: path to the HTML file
    """
    if sys.platform == "darwin":
        wb = webbrowser.get("safari")
        path_to_open = f"file://{path}"
    else:
        wb = webbrowser.get()
        path_to_open = path

    wb.open(path_to_open)


def check_if_create_new(title: str, messages_count: int) -> bool:
    """Checks if the HTML output file for a given chat exists and compares it with the chat's messages

    :param title: name of the chat
    :param messages_count: current number of messages in the chat
    :return: True if the HTML file doesn't exist or the number of messages differs (a new file should be created),
             False if the existing HTML file exists and has current data
    """
    file_path = get_file_path(title)

    if os.path.exists(file_path):
        html_messages_count = get_messages_from_html(file_path)
        if messages_count == html_messages_count:
            return False
    return True


def get_file_path(title: str) -> Path:
    """Returns a file_path of the chosen chat title"""
    return home / "output" / f"{title}.html"


def change_name(name: str) -> str:
    """Removes non-english characters from a name"""
    return name.translate(TRANSLATION_TABLE).lower()
