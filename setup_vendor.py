#!/usr/bin/env python3
"""Download vendor JavaScript libraries for offline use."""

import urllib.request
import json
from pathlib import Path

VENDOR_DIR = Path(__file__).parent / "ui" / "vendor"
VENDOR_DIR.mkdir(parents=True, exist_ok=True)

files = {
    "alpine.min.js": "https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js",
    "prism.css": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css",
    "prism.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js",
    "prism-python.min.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js",
    "prism-javascript.min.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js",
    "prism-typescript.min.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-typescript.min.js",
    "prism-bash.min.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js",
    "prism-json.min.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js",
    "prism-yaml.min.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js",
    "prism-sql.min.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js",
    "prism-markup.min.js": "https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markup.min.js",
    "marked.min.js": "https://cdn.jsdelivr.net/npm/marked/marked.min.js",
}

print("Downloading vendor files...")
for filename, url in files.items():
    filepath = VENDOR_DIR / filename
    if filepath.exists():
        print(f"  [OK] {filename} (already exists)")
    else:
        try:
            print(f"  [DL] {filename}...", end="", flush=True)
            urllib.request.urlretrieve(url, filepath)
            print(" OK")
        except Exception as e:
            print(f" ERROR: {e}")

print(f"\nVendor files ready in {VENDOR_DIR}")
