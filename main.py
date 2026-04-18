import sys
import os
import argparse
from pathlib import Path
import webview
from indexer import build_index
from api import API

try:
    import setup_vendor
except ImportError:
    pass


def resource_path(rel):
    """Get absolute path to resource (works when bundled with PyInstaller)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base, rel)


def ensure_vendor_files():
    """Download vendor files if they don't exist."""
    vendor_dir = Path(resource_path("ui/vendor"))
    required_files = ["alpine.min.js", "prism.js", "prism.css", "marked.min.js"]

    if not all((vendor_dir / f).exists() for f in required_files):
        print("Setting up vendor files...")
        try:
            import setup_vendor as sv
            sv.VENDOR_DIR.mkdir(parents=True, exist_ok=True)
            for filename, url in sv.files.items():
                filepath = sv.VENDOR_DIR / filename
                if not filepath.exists():
                    print(f"  Downloading {filename}...")
                    import urllib.request
                    urllib.request.urlretrieve(url, filepath)
        except Exception as e:
            print(f"Warning: Could not download vendor files: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (F12 dev tools)")
    args = parser.parse_args()

    ensure_vendor_files()

    index = build_index()
    api = API(index)
    window = webview.create_window(
        "Claude Code Chat Browser",
        resource_path("ui/index.html"),
        js_api=api,
        min_size=(1200, 700),
    )

    webview.start(debug=args.debug)


if __name__ == "__main__":
    main()
