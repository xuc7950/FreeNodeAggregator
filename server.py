import threading
import logging
from pathlib import Path
from flask import Flask, send_file, abort, request, redirect

BASE_DIR = Path(__file__).parent.resolve()

app = Flask(__name__)

@app.before_request
def log_request():
    logging.info("HTTP %s %s from %s", request.method, request.path, request.remote_addr)

@app.route("/")
def index():
    return redirect("https://github.com/xuc7950/FreeNodeAggregator", code=302)

@app.route("/free_nodes_raw.txt")
def free_nodes_raw():
    file_path = BASE_DIR / "free_nodes_raw.txt"
    if not file_path.exists() or not file_path.is_file():
        abort(404)
    return send_file(file_path, mimetype="text/plain; charset=utf-8")

@app.route("/free_nodes_filtered.txt")
def free_nodes_filtered_txt():
    file_path = BASE_DIR / "free_nodes_filtered.txt"
    if not file_path.exists() or not file_path.is_file():
        abort(404)
    return send_file(file_path, mimetype="text/plain; charset=utf-8")

@app.route("/free_nodes_filtered.csv")
def free_nodes_filtered_csv():
    file_path = BASE_DIR / "free_nodes_filtered.csv"
    if not file_path.exists() or not file_path.is_file():
        abort(404)
    return send_file(file_path, mimetype="text/csv; charset=utf-8")

@app.errorhandler(404)
def not_found(_):
    return "Not Found", 404

def run_server(host="0.0.0.0", port=8000):
    app.run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )

def start_server(host="0.0.0.0", port=8000, daemon=True):
    thread = threading.Thread(
        target=run_server,
        kwargs={"host": host, "port": port},
        daemon=daemon,
        name="flask-server",
    )
    thread.start()
    return thread
