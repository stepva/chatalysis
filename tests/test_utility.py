import os
from pathlib import Path
from chatalysis.utils.utility import change_name, is_latest_version, get_file_path


def test_change_name():
    assert change_name("Štěpán Vácha") == "stepanvacha"
    assert change_name("Filip    Miškařík") == "filipmiskarik"
    assert change_name("Morgan Freeman") == "morganfreeman"


def test_get_file_path():
    root = Path(__file__).parent.parent.absolute()

    assert get_file_path("Štěpán Vácha", "Messenger") == root / "output" / "Messenger" / "Štěpán Vácha.html"
    assert get_file_path("Štěpán Vácha", "Instagram") == root / "output" / "Instagram" / "Štěpán Vácha.html"

    # check if the output folders for different sources were created
    assert os.path.exists(root / "output" / "Messenger")
    assert os.path.exists(root / "output" / "Instagram")
