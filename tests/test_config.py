import os
import shutil
import pytest
from pathlib import Path
from chatalysis.utils.config import Config, config_dir_current
from chatalysis import __version__

config = Config(Path(f"tests/test_data/config_empty/{__version__}"))


def test_create_new():
    assert os.path.exists(f"tests/test_data/config_empty/{__version__}/config.ini")

    # check if the config contains default values
    assert not config.load("print_stacktrace", "dev", True)
    assert config.load("messenger", "Source_dirs") == os.getcwd()


def test_load():
    # test whether loading config items doesn't throw exceptions
    config.load("messenger", "Source_dirs")
    config.load("instagram", "Source_dirs")

    # try to load a value which isn't in the default config
    with pytest.raises(KeyError):
        config.load("source_abcd", "Source_dirs")


def test_load_boolean():
    assert isinstance(config.load("print_stacktrace", "dev"), str)
    assert isinstance(config.load("print_stacktrace", "dev", True), bool)

    config.save("print_stacktrace", "yes", "dev")
    assert config.load("print_stacktrace", "dev", True)

    config.save("print_stacktrace", "1", "dev")
    assert config.load("print_stacktrace", "dev", True)

    config.save("print_stacktrace", "off", "dev")
    assert not config.load("print_stacktrace", "dev", True)

    config.save("print_stacktrace", "false", "dev")
    assert not config.load("print_stacktrace", "dev", True)


def test_save():
    # save a value to an already existing item
    config.save("print_stacktrace", "yes", "dev")
    assert config.load("print_stacktrace", "dev", True)

    # save a new item to en existing section
    config.save("source_new", "path", "Source_dirs")
    assert config.load("source_new", "Source_dirs") == "path"

    # create a new item and section
    config.save("new_item", "value", "new_section")
    assert config.load("new_item", "new_section") == "value"

    # check if the items were saved to the config file by loading the value in a second Config object
    config2 = Config(Path(f"tests/test_data/config_empty/{__version__}"))
    assert config2.load("source_new", "Source_dirs") == "path"
    assert config2.load("new_item", "new_section") == "value"


def test_create_copy_from_previous():
    config_new = Config(Path(f"tests/test_data/config/{__version__}"))
    assert os.path.exists(f"tests/test_data/config/{__version__}/config.ini")

    # check if values were copied from an older config file
    assert config_new.load("messenger", "Source_dirs") == "source1"
    assert config_new.load("instagram", "Source_dirs") == "source2"

    # check if values which are no longer present in the default config in the current version
    # were not copied
    with pytest.raises(KeyError):
        config_new.load("item1", "DEFAULT")
    with pytest.raises(KeyError):
        config_new.load("item2", "old_category")

    # load a config item which wasn't copied from the previous config
    # should therefore be loaded from the default
    assert config_new.load("print_stacktrace", "dev") == "no"
    assert not config_new.load("print_stacktrace", "dev", True)

    shutil.rmtree(f"tests/test_data/config/{__version__}")


def test_try_create_copy_from_previous():
    # try creating a copy from previous config (the directory exists, but the file doesn't)
    # use the default config instead

    new_dir = Path("tests/test_data/config/1.0.5")
    new_dir.mkdir(parents=True)

    config_new = Config(Path(f"tests/test_data/config/{__version__}"))
    assert os.path.exists(f"tests/test_data/config/{__version__}/config.ini")

    # check if the config contains default values
    assert not config_new.load("print_stacktrace", "dev", True)
    assert config_new.load("messenger", "Source_dirs") == os.getcwd()

    new_dir.rmdir()


def test_default_config_file_existence():
    Config()
    assert os.path.exists(config_dir_current)
    assert os.path.exists(config_dir_current.parent)
    assert os.path.exists(config_dir_current / "config.ini")


def test_clean_up():
    # this is a separate function which ensures that the cleanup will happen even if some test fails
    if os.path.exists("tests/test_data/config/1.0.5"):
        shutil.rmtree("tests/test_data/config/1.0.5")
    if os.path.exists(f"tests/test_data/config/{__version__}"):
        shutil.rmtree(f"tests/test_data/config/{__version__}")
    if os.path.exists(f"tests/test_data/config_empty/{__version__}"):
        shutil.rmtree(f"tests/test_data/config_empty/{__version__}")
