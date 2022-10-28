import os
import sys
import webbrowser
from pathlib import Path

from utils.const import TRANSLATION_TABLE

home = Path(__file__).parent.parent.parent.absolute()


def html_spaces(n: int) -> str|int:
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
    return name.translate(name.maketrans(TRANSLATION_TABLE)).lower()


def list_folder(path: Path) -> list[str]:
    """Lists the names of all files / subdirectories in a directory excluding the 'DS_Store' files from macOS.

    :param path: path to the directory
    :return: list of strings with the file names
    """
    return [str(folder) for folder in os.listdir(path) if str(folder).find("DS_Store") == -1]
