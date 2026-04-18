#!/usr/bin/env python3
"""Development server with auto-reload on file changes."""

import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, process=None):
        self.process = process

    def on_modified(self, event):
        if event.is_directory:
            return
        # Only watch Python and JS files
        if event.src_path.endswith((".py", ".js", ".css", ".html")):
            rel_path = Path(event.src_path).relative_to(Path.cwd())
            print(f"\n[RELOAD] {rel_path} changed, restarting...\n")
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except:
                    self.process.kill()
            self.process = start_app()


def start_app():
    """Start the main.py process."""
    return subprocess.Popen([sys.executable, "main.py"])


if __name__ == "__main__":
    print("Starting CCB in dev mode with auto-reload...")

    process = start_app()

    # Watch current directory for changes
    handler = ReloadHandler(process)
    observer = Observer()
    observer.schedule(handler, ".", recursive=True)
    observer.daemon = True
    observer.start()

    try:
        # Keep the process alive until it exits
        while process and process.poll() is None:
            import time
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nShutting down...")
        observer.stop()
        if process and process.poll() is None:
            process.terminate()
            process.wait()
        observer.join(timeout=1)
    finally:
        print("Goodbye.")
