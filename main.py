import sys
import os
import argparse
import subprocess
import time
from pathlib import Path
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


def use_headless():
    return sys.platform == "linux"


def run_with_autoreload(extra_args):
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("watchdog not installed; running without auto-reload")
        subprocess.run([sys.executable, __file__] + extra_args)
        return

    class ReloadHandler(FileSystemEventHandler):
        def __init__(self):
            self.process = self._start()

        def _start(self):
            return subprocess.Popen([sys.executable, __file__] + extra_args)

        def on_modified(self, event):
            if event.is_directory:
                return
            if event.src_path.endswith((".py", ".js", ".css", ".html")):
                rel = Path(event.src_path).relative_to(Path.cwd())
                print(f"\n[RELOAD] {rel} changed, restarting...\n")
                if self.process.poll() is None:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=2)
                    except Exception:
                        self.process.kill()
                self.process = self._start()

    handler = ReloadHandler()
    observer = Observer()
    observer.schedule(handler, ".", recursive=True)
    observer.daemon = True
    observer.start()
    print("Auto-reload active. Ctrl+C to stop.")
    try:
        while handler.process.poll() is None:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        if handler.process.poll() is None:
            handler.process.terminate()
            handler.process.wait()
        observer.join(timeout=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (F12 dev tools)")
    parser.add_argument("--serve", action="store_true", help="Force headless/browser mode")
    parser.add_argument("--port", type=int, default=5000, help="Port for headless mode (default: 5000)")
    parser.add_argument("--dev", action="store_true", help="Auto-reload on file changes")
    args = parser.parse_args()

    if args.dev:
        extra = [a for a in sys.argv[1:] if a != "--dev"]
        run_with_autoreload(extra)
        return

    ensure_vendor_files()

    index = build_index()
    api = API(index)

    if use_headless() or args.serve:
        from server import run_server
        run_server(api, Path(resource_path("ui")), port=args.port)
    else:
        import webview
        window = webview.create_window(
            "Claude Code Chat Browser",
            resource_path("ui/index.html"),
            js_api=api,
            min_size=(1200, 700),
        )
        webview.start(debug=args.debug)


if __name__ == "__main__":
    main()
