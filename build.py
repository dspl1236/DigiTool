"""
build.py — DigiTool PyInstaller build script.
Produces: dist/DigiTool-v{version}.exe  (Windows)
          dist/DigiTool-v{version}       (Linux/Mac)

Usage:
    python build.py
"""

import os
import sys
import shutil
import subprocess

# Read version from digitool/version.py without importing PyQt5
def read_version():
    path = os.path.join(os.path.dirname(__file__), "digitool", "version.py")
    with open(path) as f:
        for line in f:
            if line.startswith("APP_VERSION"):
                return line.split("=")[1].strip().strip("\"'")
    return "0.0.0"

VERSION = read_version()
IS_WIN  = sys.platform == "win32"
EXE_NAME = f"DigiTool-v{VERSION}"


def clean():
    for d in ["build", "dist", "__pycache__"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)


def build():
    print(f"=== DigiTool Build  v{VERSION} ===")
    clean()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", EXE_NAME,
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.QtWidgets",
        "digitool/main.py",
    ]

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, check=True)

    exe = os.path.join("dist", EXE_NAME + (".exe" if IS_WIN else ""))
    if os.path.exists(exe):
        size_mb = os.path.getsize(exe) / 1_048_576
        print(f"\n✔  Built: {exe}  ({size_mb:.1f} MB)")
    else:
        print("✘  Build failed — exe not found")
        sys.exit(1)

    # Write version file for CI to pick up
    with open(os.path.join("dist", "version.txt"), "w") as f:
        f.write(f"version={VERSION}\nexe={EXE_NAME}\n")


if __name__ == "__main__":
    build()
