import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class SessionMetadata:
    def __init__(
        self,
        id: str,
        project_path: str,
        project_name: str,
        name: str,
        first_timestamp: str,
        last_timestamp: str,
        message_count: int,
        total_tokens: int,
        searchable_text: str,
    ):
        self.id = id
        self.project_path = project_path
        self.project_name = project_name
        self.name = name
        self.first_timestamp = first_timestamp
        self.last_timestamp = last_timestamp
        self.message_count = message_count
        self.total_tokens = total_tokens
        self.searchable_text = searchable_text

    def to_dict(self):
        return {
            "id": self.id,
            "project_path": self.project_path,
            "project_name": self.project_name,
            "name": self.name,
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "searchable_text": self.searchable_text,
        }


def _parse_jsonl_file(jsonl_path: Path) -> list[dict]:
    """Parse JSONL file, return list of parsed JSON objects."""
    entries = []
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error parsing {jsonl_path}: {e}")
    return entries


def _extract_session_name(entries: list[dict], first_user_text: str) -> str:
    """Extract session name from entries: custom-title > agent-name > slug > first user prompt."""
    agent_name = ""
    for entry in entries:
        if entry.get("type") == "custom-title":
            title = entry.get("customTitle", "").strip()
            if title:
                return title
        if entry.get("type") == "agent-name" and not agent_name:
            agent_name = entry.get("agentName", "").strip()
    if agent_name:
        return agent_name
    for entry in entries:
        if entry.get("slug"):
            return entry["slug"]
    return first_user_text[:60].strip()


def _extract_first_user_text(entries: list[dict]) -> str:
    """Extract first user message for search indexing."""
    for entry in entries:
        if entry.get("type") == "user":
            msg = entry.get("message", {})
            if isinstance(msg.get("content"), str):
                return msg["content"][:200]
    return ""


def _merge_assistant_pairs(entries: list[dict]) -> list[dict]:
    """
    Merge paired assistant entries that share the same message.id.
    One API response = two entries: first has thinking, second has text/tool_use.
    """
    pending = {}
    merged = []

    for entry in entries:
        if entry.get("type") == "assistant":
            msg_id = entry.get("message", {}).get("id")
            if msg_id:
                if msg_id in pending:
                    # Second part of pair — merge content and emit
                    pending[msg_id]["message"]["content"].extend(
                        entry.get("message", {}).get("content", [])
                    )
                    merged.append(pending.pop(msg_id))
                else:
                    # First part of pair — store
                    pending[msg_id] = entry
            else:
                merged.append(entry)
        else:
            merged.append(entry)

    # Emit any pending (shouldn't happen, but handle it)
    for entry in pending.values():
        merged.append(entry)

    return merged


def _build_turn(entry: dict) -> Optional[dict]:
    """Convert JSONL entry to a turn dict for display."""
    entry_type = entry.get("type")

    if entry_type == "user":
        msg = entry.get("message", {})
        content = msg.get("content")
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        elif not isinstance(content, list):
            content = []
        return {
            "role": "user",
            "timestamp": entry.get("timestamp"),
            "content": content,
        }

    if entry_type == "assistant":
        msg = entry.get("message", {})
        return {
            "role": "assistant",
            "timestamp": entry.get("timestamp"),
            "model": msg.get("model"),
            "usage": msg.get("usage", {}),
            "content": msg.get("content", []),
        }

    return None


def load_session_metadata(jsonl_path: Path) -> Optional[SessionMetadata]:
    """Parse JSONL, extract metadata: name, timestamps, token count."""
    entries = _parse_jsonl_file(jsonl_path)
    if not entries:
        return None

    # Extract project path from cwd field (most reliable)
    project_path = ""
    for entry in entries:
        cwd = entry.get("cwd")
        if cwd:
            project_path = cwd.replace("\\", "/")
            break

    first_user_text = _extract_first_user_text(entries)
    session_name = _extract_session_name(entries, first_user_text)

    first_timestamp = ""
    last_timestamp = ""
    message_count = 0
    total_tokens = 0

    # Build full-text search index from all content
    searchable_parts = [first_user_text]

    for entry in entries:
        ts = entry.get("timestamp")
        if ts and not first_timestamp:
            first_timestamp = ts
        if ts:
            last_timestamp = ts

        if entry.get("type") in ("user", "assistant"):
            message_count += 1

        if entry.get("type") == "assistant":
            usage = entry.get("message", {}).get("usage", {})
            total_tokens += usage.get("output_tokens", 0)

            # Index assistant content
            msg = entry.get("message", {})
            for block in msg.get("content", []):
                if block.get("type") == "text":
                    searchable_parts.append(block.get("text", ""))
                elif block.get("type") == "thinking":
                    searchable_parts.append(block.get("thinking", ""))

        elif entry.get("type") == "user":
            # Index user content
            msg = entry.get("message", {})
            content = msg.get("content")
            if isinstance(content, str):
                searchable_parts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        searchable_parts.append(block.get("text", ""))

    path_parts = project_path.split("/")
    if len(path_parts) >= 2:
        project_name = "/".join(path_parts[-2:])
    else:
        project_name = path_parts[-1] if path_parts else "unknown"
    searchable_text = " ".join(searchable_parts)

    return SessionMetadata(
        id=jsonl_path.stem,
        project_path=project_path,
        project_name=project_name,
        name=session_name or "untitled",
        first_timestamp=first_timestamp,
        last_timestamp=last_timestamp,
        message_count=message_count,
        total_tokens=total_tokens,
        searchable_text=searchable_text,
    )


def load_session_full(jsonl_path: Path) -> Optional[dict]:
    """Parse JSONL, return full session with merged turns."""
    entries = _parse_jsonl_file(jsonl_path)
    if not entries:
        return None

    merged = _merge_assistant_pairs(entries)

    project_path = ""
    for entry in entries:
        cwd = entry.get("cwd")
        if cwd:
            project_path = cwd.replace("\\", "/")
            break

    first_user_text = _extract_first_user_text(entries)
    session_name = _extract_session_name(entries, first_user_text)

    turns = []
    for entry in merged:
        # Skip non-turn entries
        if entry.get("type") not in ("user", "assistant"):
            continue
        turn = _build_turn(entry)
        if turn:
            turns.append(turn)

    # Sort turns by timestamp to ensure proper conversation order
    turns.sort(key=lambda t: t.get("timestamp", ""))

    return {
        "id": jsonl_path.stem,
        "name": session_name or "untitled",
        "project_path": project_path,
        "turns": turns,
    }


def scan_projects(claude_dir: Path) -> list[SessionMetadata]:
    """Scan ~/.claude/projects for all sessions, return SessionMetadata list."""
    projects_dir = claude_dir / "projects"
    if not projects_dir.exists():
        print(f"Projects dir not found: {projects_dir}")
        return []

    sessions = []
    project_count = 0
    file_count = 0

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        project_count += 1
        for jsonl_file in project_dir.glob("*.jsonl"):
            file_count += 1
            metadata = load_session_metadata(jsonl_file)
            if metadata:
                sessions.append(metadata)
            else:
                print(f"Failed to parse: {jsonl_file}")

    print(f"Scanned {project_count} projects, {file_count} JSONL files, found {len(sessions)} sessions")
    return sessions
