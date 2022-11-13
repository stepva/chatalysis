import os
import sys
import requests
import webbrowser
from pathlib import Path

from utils.const import TRANSLATE_SPECIAL_CHARS
from __init__ import __version__

home = Path(__file__).parent.parent.parent.absolute()


def html_spaces(n: int) -> str | int:
    """Splits number by thousands with a space"""
    return "{0:n}".format(n) if n != 1 else n


def open_html(path: str | Path) -> None:
    """Opens the HTML file in a browser

    :param path: path to the HTML file
    """
    if sys.platform == "darwin":
        wb = webbrowser.get("safari")
        path_to_open = f"file://{path}"
    else:
        wb = webbrowser.get()
        path_to_open = str(path)

    wb.open(path_to_open)


def get_file_path(title: str, source_name: str) -> Path:
    """Returns a file_path of the chosen chat title
    :param title: name of the chat
    :param source_name: name of the message source
    """
    file_path = home / "output" / source_name / f"{title}.html"
    file_path.parent.mkdir(parents=True, exist_ok=True)  # create source folder in "output" folder
    return file_path


def change_name(name: str) -> str:
    """Removes non-english characters from a name"""
    return name.translate(TRANSLATE_SPECIAL_CHARS).lower()


def list_folder(path: Path) -> list[str]:
    """Lists the names of all files / subdirectories in a directory excluding the 'DS_Store' files from macOS.

    :param path: path to the directory
    :return: list of strings with the file names
    """
    return [str(folder) for folder in os.listdir(path) if str(folder).find("DS_Store") == -1]


def is_latest_version() -> bool:
    """Checks if the current version is the latest available on GitHub

    :returns: True if current version == latest or if connection could not be established
    """
    try:
        latest = requests.get("https://api.github.com/repos/stepva/chatalysis/releases/latest")
    except requests.exceptions.ConnectionError:
        return True

    latest_version = latest.json()["name"]
    return latest_version == __version__


def download_latest() -> None:
    """Downloads the latest version of chatalysis via browser"""
    latest = requests.get("https://api.github.com/repos/stepva/chatalysis/releases/latest").json()["name"]
    webbrowser.open(f"https://github.com/stepva/chatalysis/archive/refs/tags/{latest}.zip")


def creation_date(path_to_file: Path) -> float:
    """
    Note: stolen from the internets
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if sys.platform == "win32" or sys.platform == "cygwin":
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            # using getattr() because mypy is dumb :) see https://github.com/python/mypy/issues/8823
            return getattr(stat, "st_birthtime")
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return getattr(stat, "st_mtime")
