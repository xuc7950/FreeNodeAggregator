# AGENTS.md

## Cursor Cloud specific instructions

### Overview

FreeNodeAggregator is a single-process Python application that fetches, merges, deduplicates, and optionally speed-tests free proxy subscription nodes. It includes a Flask HTTP server (default port 2352) that serves subscription files and a Config Manager web UI.

### Running the application

```bash
pip install -r requirements.txt
python3 main.py                    # uses config.json by default
python3 main.py -c config_dev.json # use a custom config for dev
```

- The Flask server starts automatically in a daemon thread on the port specified in config (`"port": 2352`).
- `main.py` runs an infinite loop: first-run fetch, then periodic re-fetch at the configured `update_time` and loop testing at `loop_test_interval`.

### Key gotchas

- **`xray-knife` permissions**: The Linux binary at `tools/Linux/xray-knife` ships without execute permission. You must run `chmod +x tools/Linux/xray-knife` before the app can use test mode `"basic"` or `"full"`. If you don't need speed testing, set `test.mode` to `"none"` in your config.
- **`blinker` system package conflict**: On Ubuntu-based environments, `pip install` may fail with "Cannot uninstall blinker" because the system-managed version lacks a RECORD file. Fix: `pip install --ignore-installed blinker` before running `pip install -r requirements.txt`.
- **No lint/test/build tooling**: This codebase has no linter config, no automated test suite, and no build step. It is a pure Python app that runs directly.
- **External URL timeouts**: `main.py` fetches from ~20 external subscription URLs on startup. Many may time out or fail; the app handles this gracefully. For faster dev startup, use a config with fewer (or no) query sources and `test.mode` set to `"none"`.
- **Config Manager web UI** is served at `http://127.0.0.1:<port>/` (the `index.html` file). It requires password setup on first visit (or via the `/api/password/init` endpoint).
- **Config hot-reload**: `main.py` detects changes to `config.json` automatically between loop iterations (no restart needed for most settings; port changes require restart).

### API endpoints

See `server.py` for the full list. Key endpoints:
- `GET /` — Config Manager UI
- `GET /api/config` — Read current config
- `POST /api/config/save` — Save config
- `GET /free_nodes_raw.txt` — Raw merged nodes
- `GET /free_nodes_filtered.txt` — Filtered nodes (after testing)
