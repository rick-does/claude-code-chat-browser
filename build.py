#!/usr/bin/env python3
"""Build standalone .exe for Claude Code Browser."""

import subprocess
import sys
import os
from pathlib import Path

def build():
    script = Path(__file__).parent / "main.py"
    ui_dir = Path(__file__).parent / "ui"

    # PyInstaller uses ; on Windows, : on Unix
    separator = ";" if sys.platform == "win32" else ":"

    cmd = [
        sys.executable,
        "-m",
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "CCB",
        "--add-data", f"{ui_dir}{separator}ui",
        "--hidden-import=pyperclip",
        "--collect-all=pywebview",
        str(script),
    ]

    print(f"Building CCB executable...\n")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    if result.returncode == 0:
        dist_dir = Path(__file__).parent / "dist"
        exe = dist_dir / ("CCB.exe" if sys.platform == "win32" else "CCB")
        print(f"\n✓ Build successful!")
        print(f"  Executable: {exe}")
        print(f"  Run: {exe}")
    else:
        print(f"\n✗ Build failed with return code {result.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    build()
