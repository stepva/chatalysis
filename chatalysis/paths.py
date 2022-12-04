import os
import sys
from pathlib import Path

# Pyinstaller creates a temp folder and stores path in _MEIPASS
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    HOME = Path(getattr(sys, "_MEIPASS"))
    if sys.platform == "darwin":
        exe_location = Path(sys.executable).parent.parent.parent.absolute()
    else:
        exe_location = Path(os.getcwd())
    OUTPUT_DIR = exe_location / "output"
else:
    HOME = Path(__file__).parent.parent.absolute()
    OUTPUT_DIR = HOME / "output"
