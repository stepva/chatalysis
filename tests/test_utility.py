from chatalysis.utils.utility import change_name, is_latest_version


def test_change_name():
    assert change_name("Štěpán Vácha") == "stepanvacha"
    assert change_name("Filip    Miškařík") == "filipmiskarik"
    assert change_name("Morgan Freeman") == "morganfreeman"


def test_is_latest_version():
    assert is_latest_version()
