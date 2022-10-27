import appdirs
import configparser
import os
from pathlib import Path

from __init__ import __version__
from utils.utility import list_folder

config_dir = Path(appdirs.user_config_dir("Chatalysis"))
config_dir_current = config_dir / __version__
config_dir_current.mkdir(parents=True, exist_ok=True)
config_file = config_dir_current / "config.ini"


class Config:
    """Simple class for saving & loading config items"""

    DEFAULT_CONFIG = {
        "General": {"force_generate": "no"},
        "Source_dirs": {"Messenger": os.getcwd(), "Instagram": os.getcwd()},
    }

    def __init__(self):
        self._parser = configparser.ConfigParser()

        if os.path.exists(config_file):
            self._parser.read(config_file)
        else:
            self._create()

    def save(self, item: str, value: str, section: str = "General"):
        """Save a config item

        :param item: name of the item
        :param section: name of the section in which the item is stored
        :param value: value of the config item
        """
        if not self._parser.has_section(section):
            self._parser.add_section(section)

        self._parser.set(section, item, value)
        with open(config_file, "w") as cfg:
            self._parser.write(cfg)

    def load(self, item: str, section: str = "General", is_bool: bool = False):
        """Loads a config item

        :param item: name of the item
        :param section: name of the config section in which the item is stored
        :param is_bool: True if value of requested item is boolean
                        required for correct type conversion as bool('False') == True
        :returns: value of the config item
        """
        if self._parser.has_option(section, item):
            val = self._parser[section].getboolean(item) if is_bool else self._parser[section][item]
        else:
            self.save(item, self.DEFAULT_CONFIG[section][item], section)
            val = self._parser[section].getboolean(item) if is_bool else self._parser[section][item]
        return val

    def _create(self):
        """Create the config file and initialize it with default values"""
        config_versions = sorted(list_folder(config_dir))

        if len(config_versions) > 1:
            # take config values from config file for previous version of chatalysis
            # that are still present (defined) in the current version
            prev_config = Path(config_dir, str(config_versions[-2]), "config.ini")
            prev_parser = configparser.ConfigParser()
            prev_parser.read(prev_config)

            config = dict()
            for section in [sec for sec in prev_parser.sections() if sec in self.DEFAULT_CONFIG]:
                config.update({section: {}})
                for item in [it for it in prev_parser.options(section) if it in self.DEFAULT_CONFIG[section]]:
                    config[section].update({item: prev_parser.get(section, item)})

            self._parser.read_dict(config)
        else:
            self._parser.read_dict(self.DEFAULT_CONFIG)

        with open(config_file, "w") as cfg:
            self._parser.write(cfg)
