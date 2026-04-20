import threading
import webbrowser
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, Response


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
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    print(f"CCB running at {url}")
    app.run(host="localhost", port=port, debug=False, use_reloader=False)
