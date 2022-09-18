import appdirs
import configparser
import os
from pathlib import Path

from __init__ import __version__

config_dir = Path(appdirs.user_config_dir("Chatalysis", version=__version__))
config_file = config_dir / "config.ini"


class Config:
    """Simple class for saving & loading config items"""

    def __init__(self):
        self._parser = configparser.ConfigParser()

        if os.path.exists(config_file):
            self._parser.read(config_file)
        else:
            self._create()

    def save(self, item: str, value: str):
        """Save a config item

        :param item: name of the item
        :param value: value of the config item
        """
        self._parser["DEFAULT"][item] = value
        with open(config_file, "w") as cfg:
            self._parser.write(cfg)

    def load(self, item: str, is_bool: bool = False):
        """Loads a config item

        :param item: name of the item
        :param is_bool: True if value of requested item is boolean
                        required for correct type conversion as bool('False') == True
        :returns: value of the config item
        """
        if is_bool:
            return self._parser["DEFAULT"].getboolean(item)
        return self._parser["DEFAULT"][item]

    def _create(self):
        """Create the config file and initialize it with default values"""
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.touch(exist_ok=True)

        self._parser["DEFAULT"] = {"last_source_dir": os.getcwd(), "force_generate": "no"}
