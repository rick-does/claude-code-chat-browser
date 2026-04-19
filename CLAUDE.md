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

## Recent Features & Improvements

### Chat Display
- **Turn ordering:** Turns are now sorted by timestamp to ensure proper conversation interleaving (user→assistant→user, etc.)
- **Message numbering:** Each user and assistant message is numbered (USER (1), ASSISTANT (2), etc.) for easy reference when copying sections

### Theme Support
- **Light/Dark mode toggle:** Button in header next to refresh (◑/◯ icons)
- **Theme persistence:** User's theme choice is saved to localStorage
- **CSS variables:** All colors use theme-aware variables for seamless light/dark switching
- **Code blocks:** Always use dark theme in light mode for readability

### Styling
- **Text colors:** Removed yellow/purple accent colors from prose text (headings, strong, em) to use theme-aware text colors
- **Sidebar footer:** Fixed at 50px height, always stuck to bottom (uses CSS Grid layout)
- **Search highlights:** Bold text for matches, themed background for current match, wraps around at edges
- **Scrollbars:** Styled to match theme colors in all scrollable areas

### UI Polish
- **Button styling:** Consistent gray buttons (dark theme-aware) for theme toggle and refresh
- **Context menu:** Styled with theme colors instead of hardcoded values
- **Search controls:** Themed background and text colors for match navigation
