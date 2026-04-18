import subprocess
import time
import sys
from pathlib import Path
from typing import Optional
from indexer import Index
from loader import load_session_full

try:
    import pyperclip
except ImportError:
    pyperclip = None

# Dev mode: track startup time for reload detection
_startup_time = time.time()


class API:
    def __init__(self, index: Index):
        self.index = index

    def get_projects(self) -> list[dict]:
        """Return list of projects with session counts."""
        return self.index.get_projects()

    def get_chats(self, project: Optional[str] = None, query: Optional[str] = None) -> list[dict]:
        """Return filtered list of chats."""
        return self.index.get_chats(project, query)

    def get_chat(self, session_id: str) -> Optional[dict]:
        """Load full chat transcript by session ID."""
        claude_dir = Path.home() / ".claude"
        projects_dir = claude_dir / "projects"

        # Find the JSONL file for this session ID
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            jsonl_path = project_dir / f"{session_id}.jsonl"
            if jsonl_path.exists():
                return load_session_full(jsonl_path)

        return None

    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard."""
        if not pyperclip:
            return False
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False

    def get_version(self) -> float:
        """Return startup time for dev reload detection."""
        return _startup_time

    def save_last_chat(self, chat_id: str) -> bool:
        """Save last opened chat to a file for persistence across restarts."""
        try:
            import json
            config_file = Path.home() / ".claude" / "ccb_state.json"
            config_file.write_text(json.dumps({"last_chat": chat_id}))
            return True
        except Exception:
            return False

    def get_last_chat(self) -> str:
        """Retrieve last opened chat from file."""
        try:
            import json
            config_file = Path.home() / ".claude" / "ccb_state.json"
            if config_file.exists():
                data = json.loads(config_file.read_text())
                return data.get("last_chat", "")
        except Exception:
            pass
        return ""
