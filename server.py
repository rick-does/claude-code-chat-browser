import logging
import subprocess
import threading
import webbrowser
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, Response


def _is_wsl():
    try:
        return b"microsoft" in Path("/proc/version").read_bytes().lower()
    except OSError:
        return False


def _is_linux():
    import sys
    return sys.platform == "linux"


def _open_browser(url):
    if _is_wsl():
        subprocess.Popen(["cmd.exe", "/c", "start", url])
    else:
        webbrowser.open(url)


def run_server(api, ui_dir: Path, port: int = 5000):
    app = Flask(__name__, static_folder=None)

    @app.route("/")
    def index():
        html = (ui_dir / "index.html").read_text(encoding="utf-8")
        html = html.replace("</head>", "<script>window.CCB_HEADLESS=true;</script></head>")
        return Response(html, mimetype="text/html")

    @app.route("/<path:filename>")
    def static_files(filename):
        return send_from_directory(ui_dir, filename)

    @app.route("/api/get_projects")
    def get_projects():
        return jsonify(api.get_projects())

    @app.route("/api/get_chats")
    def get_chats():
        project = request.args.get("project") or None
        query = request.args.get("query") or None
        return jsonify(api.get_chats(project, query))

    @app.route("/api/get_chat")
    def get_chat():
        return jsonify(api.get_chat(request.args.get("session_id")))

    @app.route("/api/get_version")
    def get_version():
        return jsonify(api.get_version())

    @app.route("/api/get_last_chat")
    def get_last_chat():
        return jsonify(api.get_last_chat())

    @app.route("/api/save_last_chat", methods=["POST"])
    def save_last_chat():
        data = request.get_json() or {}
        return jsonify(api.save_last_chat(data.get("chat_id", "")))

    url = f"http://localhost:{port}"
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    print(f"CCCB running at {url}")
    if _is_wsl():
        threading.Timer(0.8, lambda: _open_browser(url)).start()
    elif _is_linux():
        import socket
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except OSError:
            ip = "unknown"
        print(f"Network access: http://{ip}:{port}")
    else:
        threading.Timer(0.8, lambda: _open_browser(url)).start()

    host = "0.0.0.0" if _is_linux() and not _is_wsl() else "localhost"
    app.run(host=host, port=port, debug=False, use_reloader=False)
