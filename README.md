# Claude Code Chat Browser (CCCB)

[![Build Executable](https://github.com/rick-does/claude-code-chat-browser/actions/workflows/build.yml/badge.svg)](https://github.com/rick-does/claude-code-chat-browser/actions/workflows/build.yml)

A lightweight desktop app for browsing, searching, and copying text from your Claude Code chat history. No cloud, no tracking—everything stays local.

## Features

- **Browse chats** — Organized by project with expandable groups
- **Full-text search** — Find conversations by name or content, with navigation wrapping
- **View transcripts** — Syntax-highlighted code blocks, expandable thinking sections, tool visualizations, message numbering
- **Copy to clipboard** — Extract text, code, or entire conversations
- **Light/Dark mode** — Toggle theme with persistent preference
- **Metadata** — See message count, token usage, and timestamps
- **Persistent state** — Remembers your last opened chat and theme preference

## Install

**Windows (Recommended):**
1. Download `CCCB.exe` from [Releases](https://github.com/rick-does/claude-code-chat-browser/releases)
2. Run it — no installation needed

**From Source:**
```bash
git clone git@github.com:rick-does/claude-code-chat-browser.git
cd claude-code-chat-browser
pip install -r requirements.txt
python main.py
```

## Usage

- **Search** — Type in the sidebar to filter chats
- **Project filter** — Select a project to narrow the list
- **Transcript search** — Use the search box in the main pane to find text within a chat; navigate with arrow buttons (wraps around at edges)
- **Message numbering** — Each user/assistant message is numbered for easy reference when copying sections
- **Light/Dark mode** — Click the theme toggle button (◑/◯) next to the refresh button to switch themes
- **Copy** — Right-click to copy selected text or entire sections
- **GitHub** — Click the footer link to report issues or request features

## Linux / WSL

On Linux and WSL, CCCB runs as a local web server instead of a desktop app. Open your browser to the URL printed on startup.

**WSL:** CCCB automatically opens your Windows browser.

**Remote Linux server (SSH):** Use an SSH tunnel so you can access the UI from your local browser — no firewall changes needed:

```bash
ssh -L 5000:localhost:5000 user@your-server
```

Then open `http://localhost:5000` in your local browser while the tunnel is active.

## Building

To create a standalone executable:

```bash
pip install -r requirements.txt
python build.py
```

Output: `dist/CCCB.exe` (Windows), `dist/CCCB` (macOS/Linux)

## Development

```bash
python main.py          # Run normally
python main.py --dev    # Run with auto-reload on file changes
python main.py --serve  # Force browser mode (test headless on any platform)
python setup_vendor.py  # Download vendor libraries
```

## Architecture

- **Backend:** Python with in-memory indexing
- **Frontend:** Alpine.js + vanilla HTML/CSS
- **Framework:** pywebview (Windows/Mac), Flask (Linux/WSL)
- **Data source:** `~/.claude` (Claude Code chat history)

## Data & Privacy

CCCB reads from your local `~/.claude` directory only—no data is sent anywhere. The app runs entirely offline.

## License

MIT
