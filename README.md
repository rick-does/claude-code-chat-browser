# Claude Code Chat Browser (CCB)

A lightweight desktop app for browsing, searching, and copying text from your Claude Code chat history. No cloud, no tracking—everything stays local.

## Features

- **Browse chats** — Organized by project with expandable groups
- **Full-text search** — Find conversations by name or content
- **View transcripts** — Syntax-highlighted code blocks, expandable thinking sections, tool visualizations
- **Copy to clipboard** — Extract text, code, or entire conversations
- **Metadata** — See message count, token usage, and timestamps
- **Persistent state** — Remembers your last opened chat

## Install

**Windows (Recommended):**
1. Download `CCB.exe` from [Releases](https://github.com/rick-does/claude-code-chat-browser/releases)
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
- **Transcript search** — Use the search box in the main pane to find text within a chat
- **Copy** — Right-click to copy selected text or entire sections
- **GitHub** — Click the footer link to report issues or request features

## Building

To create a standalone `.exe` (Windows):

```bash
pip install -r requirements.txt
python build.py
```

Output: `dist/CCB.exe`

## Architecture

- **Backend:** Python with in-memory indexing
- **Frontend:** Alpine.js + vanilla HTML/CSS
- **Framework:** pywebview (cross-platform desktop app)
- **Data source:** `~/.claude` (Claude Code chat history)

## Development

```bash
python dev.py                  # Run with auto-reload
python setup_vendor.py         # Download vendor libraries
```

## Data & Privacy

CCB reads from your local `~/.claude` directory only—no data is sent anywhere. The app runs entirely offline.

## License

MIT
