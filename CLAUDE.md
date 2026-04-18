# Claude Code Chat Browser — Development Guide

## Setup

```bash
pip install -r requirements.txt
python main.py              # Run desktop app
python dev.py              # Run with auto-reload
python setup_vendor.py     # Download vendor JS libraries (offline use)
```

## Building Standalone Executable

```bash
python build.py
```

Output: `dist/CCB.exe` (Windows), `dist/CCB` (macOS/Linux)

## Architecture

- **Backend:** Python with in-memory indexing of `~/.claude` chat history
- **Frontend:** Alpine.js + vanilla HTML/CSS/JavaScript
- **Framework:** pywebview (cross-platform desktop UI)
- **Data flow:** Scan `~/.claude/projects/*.jsonl` → Index sessions → Search in-memory

## Key Files

- `main.py` — Entry point, window setup, vendor file initialization
- `api.py` — Python API exposed to frontend via pywebview
- `indexer.py` — In-memory search index
- `loader.py` — JSONL parsing, session metadata extraction
- `ui/` — HTML/CSS/JavaScript frontend
- `build.py` — PyInstaller build script

## Development Notes

- Frontend updates reload automatically in dev mode (`python dev.py`)
- Backend restarts trigger page reload via version polling (2s interval)
- Session data is parsed fresh on each app startup (Phase 1 MVP)
- Future: Add SQLite caching layer for faster launches
- Cross-platform path handling: Always normalize to `/` internally
