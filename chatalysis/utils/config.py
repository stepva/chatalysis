import appdirs
import configparser
import os
from pathlib import Path
from typing import Dict, Any

from __init__ import __version__
from utils.utility import list_folder

config_dir_current = Path(appdirs.user_config_dir("Chatalysis")) / __version__


class Config:
    """Simple class for saving & loading config items"""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "General": {},
        "Source_dirs": {"messenger": os.getcwd(), "instagram": os.getcwd()},
        "dev": {"print_stacktrace": "no"},
    }

    def __init__(self, config_dir: Path = config_dir_current) -> None:
        config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = config_dir / "config.ini"
        self._parser = configparser.ConfigParser()

        if os.path.exists(self._config_file):
            self._parser.read(self._config_file)
        else:
            self._create()
            with open(self._config_file, "w") as cfg:
                self._parser.write(cfg)

    def save(self, item: str, value: str, section: str = "General") -> None:
        """Save a config item

        :param item: name of the item
        :param section: name of the section in which the item is stored
        :param value: value of the config item
        """
        if not self._parser.has_section(section):
            self._parser.add_section(section)

        self._parser.set(section, item, value)
        with open(self._config_file, "w") as cfg:
            self._parser.write(cfg)

    def load(self, item: str, section: str = "General", is_bool: bool = False) -> Any:
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

    def _create(self) -> None:
        """Create the config file and initialize it with default values"""
        config_dir = self._config_file.parent.parent
        config_versions = sorted([item for item in list_folder(config_dir) if os.path.isdir(config_dir / item)])

        if len(config_versions) > 1:
            # take config values from config file for previous version of chatalysis
            # that are still present (defined) in the current version
            prev_config = Path(config_dir, config_versions[-2], "config.ini")

            if not os.path.exists(prev_config):
                self._parser.read_dict(self.DEFAULT_CONFIG)
                return

            prev_parser = configparser.ConfigParser()
            prev_parser.read(prev_config)

            config: Any = dict()
            for section in [sec for sec in prev_parser.sections() if sec in self.DEFAULT_CONFIG]:
                config.update({section: {}})
                for item in [it for it in prev_parser.options(section) if it in self.DEFAULT_CONFIG[section]]:
                    config[section].update({item: prev_parser.get(section, item)})

            self._parser.read_dict(config)
        else:
            self._parser.read_dict(self.DEFAULT_CONFIG)
