import hashlib
import json
import logging
import os
import platform
import subprocess
import threading
from urllib.request import Request, urlopen
from pathlib import Path
from flask import Flask, send_file, abort, request, jsonify

BASE_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = BASE_DIR / "config.json"
DEFAULT_CONFIG_URL = "https://xuc7950.github.io/FreeNodeAggregator/config.json"
PASSWORD_ENV_KEY = "CONFIG_MGR_PASSWORD_HASH"
PASSWORD_SALT = "__config_mgr_salt__"

app = Flask(__name__)

@app.before_request
def log_request():
    logging.info("HTTP %s %s from %s", request.method, request.path, request.remote_addr)

@app.route("/")
def index():
    file_path = BASE_DIR / "index.html"
    if not file_path.exists() or not file_path.is_file():
        abort(404)
    return send_file(file_path, mimetype="text/html; charset=utf-8")

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


def _hash_password(password: str) -> str:
    return hashlib.sha256((password + PASSWORD_SALT).encode("utf-8")).hexdigest()


def _quote_posix(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def _persist_env_var(key: str, value: str) -> bool:
    system = platform.system().lower()
    os.environ[key] = value

    if system == "windows":
        # Persist to user env on Windows.
        result = subprocess.run(
            ["setx", key, value],
            capture_output=True,
            text=True,
            shell=False,
            check=False,
        )
        if result.returncode != 0:
            logging.error("setx failed: %s", (result.stderr or result.stdout).strip())
            return False
        return True

    # Linux / macOS: append or replace `export KEY=...` in common profiles.
    export_line = f"export {key}={_quote_posix(value)}"
    profile_paths = [
        Path.home() / ".profile",
        Path.home() / ".bashrc",
        Path.home() / ".zshrc",
    ]
    for profile in profile_paths:
        try:
            existing = profile.read_text(encoding="utf-8") if profile.exists() else ""
            lines = existing.splitlines()
            replaced = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"export {key}="):
                    lines[i] = export_line
                    replaced = True
            if replaced:
                new_content = "\n".join(lines) + ("\n" if lines else "")
            else:
                suffix = "\n" if existing and not existing.endswith("\n") else ""
                new_content = f"{existing}{suffix}{export_line}\n"
            profile.write_text(new_content, encoding="utf-8")
        except Exception as exc:
            logging.error("Failed to persist env var in %s: %s", profile, exc)
            return False
    return True


def _get_password_hash() -> str:
    value = os.getenv(PASSWORD_ENV_KEY, "")
    return value.strip()


def _json_error(message: str, status: int = 400):
    return jsonify({"success": False, "message": message}), status


def _load_local_config():
    if not CONFIG_PATH.exists() or not CONFIG_PATH.is_file():
        return None
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logging.error("Failed to read config.json: %s", exc)
        return None


def _save_local_config(config_obj) -> bool:
    try:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config_obj, f, ensure_ascii=False, indent=4)
            f.write("\n")
        return True
    except Exception as exc:
        logging.error("Failed to write config.json: %s", exc)
        return False


def _fetch_default_config():
    req = Request(
        DEFAULT_CONFIG_URL,
        headers={"User-Agent": "FreeNodeAggregator-ConfigManager"},
    )
    with urlopen(req, timeout=12) as resp:
        content = resp.read().decode("utf-8")
    return json.loads(content)


@app.route("/api/config", methods=["GET"])
def get_config():
    config = _load_local_config()
    if config is None:
        return _json_error("读取本地 config.json 失败", 500)
    return jsonify({"success": True, "config": config})


@app.route("/api/config/save", methods=["POST"])
def save_config():
    data = request.get_json(silent=True) or {}
    config = data.get("config")
    if not isinstance(config, dict):
        return _json_error("配置格式错误，需要对象类型")
    if not _save_local_config(config):
        return _json_error("写入本地 config.json 失败", 500)
    return jsonify({"success": True})


@app.route("/api/config/reset", methods=["POST"])
def reset_config():
    try:
        config = _fetch_default_config()
    except Exception as exc:
        logging.error("Failed to fetch remote default config: %s", exc)
        return _json_error("拉取默认配置失败", 502)
    if not isinstance(config, dict):
        return _json_error("远程默认配置格式错误", 502)
    if not _save_local_config(config):
        return _json_error("写入本地 config.json 失败", 500)
    return jsonify({"success": True, "config": config})


@app.route("/api/password/status", methods=["GET"])
def password_status():
    return jsonify({"initialized": bool(_get_password_hash())})


@app.route("/api/password/init", methods=["POST"])
def password_init():
    data = request.get_json(silent=True) or {}
    password = str(data.get("password", "")).strip()
    if not password:
        return _json_error("密码不能为空")
    if len(password) < 4:
        return _json_error("密码至少 4 位")
    if _get_password_hash():
        return _json_error("密码已初始化，请使用修改密码接口", 409)

    pw_hash = _hash_password(password)
    if not _persist_env_var(PASSWORD_ENV_KEY, pw_hash):
        return _json_error("写入环境变量失败")
    return jsonify({"success": True})


@app.route("/api/password/verify", methods=["POST"])
def password_verify():
    data = request.get_json(silent=True) or {}
    password = str(data.get("password", ""))
    stored = _get_password_hash()
    if not stored:
        return _json_error("密码未初始化", 404)
    return jsonify({"success": _hash_password(password) == stored})


@app.route("/api/password/change", methods=["POST"])
def password_change():
    data = request.get_json(silent=True) or {}
    old_password = str(data.get("old_password", ""))
    new_password = str(data.get("new_password", "")).strip()
    stored = _get_password_hash()

    if not stored:
        return _json_error("密码未初始化", 404)
    if _hash_password(old_password) != stored:
        return _json_error("当前密码错误")
    if not new_password:
        return _json_error("新密码不能为空")
    if len(new_password) < 4:
        return _json_error("新密码至少 4 位")

    new_hash = _hash_password(new_password)
    if not _persist_env_var(PASSWORD_ENV_KEY, new_hash):
        return _json_error("写入环境变量失败")
    return jsonify({"success": True})

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
