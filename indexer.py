from pathlib import Path
from typing import Optional
from loader import SessionMetadata, scan_projects


class Index:
    def __init__(self, sessions: list[SessionMetadata]):
        self.sessions = sorted(sessions, key=lambda s: s.last_timestamp, reverse=True)

    def search(self, query: str) -> list[dict]:
        """Search sessions by name and searchable_text (case-insensitive substring)."""
        if not query.strip():
            return [s.to_dict() for s in self.sessions]

        query_lower = query.lower()
        results = []

        for session in self.sessions:
            if query_lower in session.name.lower() or query_lower in session.searchable_text.lower():
                results.append(session.to_dict())

        return results

    def filter_by_project(self, project_path: str) -> list[dict]:
        """Filter sessions by project path."""
        if not project_path:
            return [s.to_dict() for s in self.sessions]

        results = []
        for session in self.sessions:
            if session.project_path.lower() == project_path.lower():
                results.append(session.to_dict())

        return results

    def get_projects(self) -> list[dict]:
        """Get unique projects with session counts."""
        projects = {}
        for session in self.sessions:
            path = session.project_path.rstrip("/\\").lower()
            if path not in projects:
                projects[path] = {
                    "path": session.project_path,
                    "name": session.project_name,
                    "session_count": 0,
                }
            projects[path]["session_count"] += 1

        return sorted(projects.values(), key=lambda p: p["name"])

    def get_chats(self, project: Optional[str] = None, query: Optional[str] = None) -> list[dict]:
        """Get chats filtered by project and/or search query."""
        results = self.sessions

        if project:
            results = [s for s in results if s.project_path.lower() == project.lower()]

        if query:
            query_lower = query.lower()
            results = [
                s
                for s in results
                if query_lower in s.name.lower() or query_lower in s.searchable_text.lower()
            ]

        return [s.to_dict() for s in results]


def build_index(claude_dir: Path = None) -> Index:
    """Scan ~/.claude and build in-memory search index."""
    if claude_dir is None:
        claude_dir = Path.home() / ".claude"

    sessions = scan_projects(claude_dir)
    return Index(sessions)
