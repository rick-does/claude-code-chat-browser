#!/usr/bin/env python3
"""Build standalone .exe for Claude Code Browser."""

import sys
from pathlib import Path
from PyInstaller.__main__ import run as pyinstaller_run

def build():
    script = Path(__file__).parent / "main.py"
    ui_dir = Path(__file__).parent / "ui"

    # PyInstaller uses ; on Windows, : on Unix
    separator = ";" if sys.platform == "win32" else ":"

    args = [
        "--onefile",
        "--windowed",
        "--name", "CCB",
        "--add-data", f"{ui_dir}{separator}ui",
        "--hidden-import=pyperclip",
        "--collect-all=pywebview",
        str(script),
    ]

    print("Building CCB executable...\n")
    try:
        pyinstaller_run(args)
        dist_dir = Path(__file__).parent / "dist"
        exe = dist_dir / ("CCB.exe" if sys.platform == "win32" else "CCB")
        print(f"\n[OK] Build successful!")
        print(f"  Executable: {exe}")
        print(f"  Run: {exe}")
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
