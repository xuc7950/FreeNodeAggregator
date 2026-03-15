<div align="center">

# FreeNodeAggregator

**Free Proxy Node Subscription Aggregator**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

A Python tool that automatically fetches, merges, tests, and deduplicates proxy nodes from multiple free sources.

English | **[简体中文](README_CN.md)**

</div>

---

## Features

| Feature | Description |
|:---:|:---|
| 🌐 **Multi-source Aggregation** | Fetch nodes from multiple free subscription sources simultaneously |
| 🔀 **Auto Deduplication** | Smart duplicate removal during merging |
| 📡 **Multi-protocol Support** | Support vmess, ss, ssr, trojan, vless protocols |
| 📦 **Standard Output** | Base64 encoded subscription content, ready to import |
| 🖥️ **Local Server** | Built-in HTTP server for subscription links |
| ⏰ **Scheduled Updates** | Automatic daily node refresh at configured time |
| 🔄 **Loop Testing** | Periodic node testing without re-fetching |
| 🔧 **Dynamic Config** | Python expressions supported in URLs |
| 🧪 **Node Testing** | Connectivity test and comprehensive speed test |
| 🚀 **Smart Filtering** | Auto-filter low-speed nodes based on threshold |
| 🐳 **Docker Support** | Full Docker compatibility |
| 🍎 **Cross-platform** | Support Windows, Linux, and macOS |
| 🎨 **Terminal Adaptation** | Auto-detect terminal capabilities for color/ASCII mode |

## Quick Start

### Option 1: Local Run

```bash
# Clone repository
git clone https://github.com/xuc7950/FreeNodeAggregator.git
cd FreeNodeAggregator

# Install dependencies
pip install -r requirements.txt

# Run with default config
python main.py
```

<details>
<summary>📖 Platform-specific Instructions</summary>

**Windows:**
```cmd
run.bat
```

**Linux/macOS:**
```bash
pip3 install -r requirements.txt
python3 main.py
```

</details>

### Option 2: Docker Deployment

```bash
# Load image
sudo docker load -i FreeNodesAggregator@0.0.2-Docker.tar

# Run container
sudo docker run --name free_node_aggregator \
  -d \
  -p 2352:2352 \
  -v /path/to/config.json:/FreeNodeAggregator/config.json \
  free_node_aggregator:0.0.2

# View logs
sudo docker logs -f free_node_aggregator
```

<details>
<summary>📖 Docker Commands</summary>

```bash
# Stop container
sudo docker stop free_node_aggregator

# Start container
sudo docker start free_node_aggregator

# Restart container
sudo docker restart free_node_aggregator

# Remove container
sudo docker rm -f free_node_aggregator
```

</details>

## Command Line Arguments

| Argument | Short | Description | Default |
|:---:|:---:|:---|:---:|
| `--config` | `-c` | Specify config file path | `config.json` |

**Usage:**

```bash
# Use default config
python main.py

# Use custom config file
python main.py --config myconfig.json
python main.py -c /path/to/config.json

# Show help
python main.py --help
```

## Configuration

### Config File Structure

```json
{
    "update_time": "03:00",
    "port": 2352,
    "loop_test_interval": 5,
    "test": {
        "mode": "full",
        "threads": 100,
        "speed_threshold": 0.2
    },
    "query_list": [
        {"url": "https://example.com/subscribe"}
    ]
}
```

### Global Parameters

| Parameter | Type | Description | Default |
|:---|:---:|:---|:---:|
| `update_time` | string | Daily update time (`HH:MM`) | `"03:00"` |
| `port` | number | HTTP server port | `2352` |
| `loop_test_interval` | number | Loop test interval in minutes | `5` |
| `test` | object | Node testing configuration | - |
| `query_list` | array | Node source list | `[]` |

### Test Parameters

| Parameter | Type | Description |
|:---|:---:|:---|
| `mode` | string | `none` / `basic` / `full` |
| `threads` | number | Concurrent test threads (recommended: 10-100) |
| `speed_threshold` | number | Minimum speed threshold in Mb/s (`full` mode only) |

**Test Modes:**

| Mode | Description |
|:---:|:---|
| `none` | Skip testing, output raw nodes directly |
| `basic` | Connectivity test only |
| `full` | Full speed test with latency, download/upload metrics, and auto-filtering |

### Node Source Configuration

**Mode 1: Direct Subscription URL**

For URLs that return node content directly:

```json
{"url": "https://example.com/nodes.txt"}
```

**Mode 2: Two-step Fetch**

For websites that require visiting a page first, then extracting subscription links:

```json
{
    "url": "https://example.com",
    "match1": "article a",
    "match2": ".content p"
}
```

| Parameter | Description |
|:---:|:---|
| `url` | Target website URL |
| `match1` | CSS selector to find subscription link on the first page |
| `match2` | CSS selector to extract node content from the second page |

**Mode 3: Dynamic URL**

Support Python expressions in URLs using `{expression}` syntax:

```json
{"url": "https://example.com/nodes_{datetime.now().strftime('%Y%m%d')}.txt"}
```

### Complete Example

```json
{
    "update_time": "03:00",
    "port": 2352,
    "loop_test_interval": 5,
    "test": {
        "mode": "full",
        "threads": 100,
        "speed_threshold": 0.2
    },
    "query_list": [
        {
            "url": "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v{datetime.now().strftime('%Y%m%d')}2"
        },
        {
            "url": "https://nodefree.me",
            "match1": "article a",
            "match2": ".section p"
        },
        {
            "url": "https://www.freev2raynode.com",
            "match1": ".col-md-3 a",
            "match2": ".post-content-content p"
        }
    ]
}
```

## Output Files

| File | Description |
|:---|:---|
| `free_nodes_raw.txt` | Raw merged nodes (untested) |
| `free_nodes_filtered.txt` | Filtered nodes after testing |
| `free_nodes_filtered.csv` | Detailed speed test results (`full` mode only) |

## Subscription URL

After running, import into your client using:

| Type | URL |
|:---:|:---|
| Local | `http://127.0.0.1:2352/free_nodes_filtered.txt` |
| LAN | `http://<YOUR_IP>:2352/free_nodes_filtered.txt` |

> 💡 **Tip**: Works best with [Karing](https://github.com/KaringX/karing), a cross-platform proxy client with a clean and intuitive interface.

## Project Structure

```
FreeNodeAggregator/
├── main.py               # Main program entry
├── utility.py            # Utility functions
├── config.json           # Configuration file
├── requirements.txt      # Python dependencies
├── run.bat               # Windows startup script
├── tools/                # Node testing tools
│   ├── Windows/          # Windows xray-knife
│   ├── Linux/            # Linux xray-knife
│   └── MacOS/            # macOS xray-knife
└── README.md             # Documentation
```

## Environment Variables

| Variable | Description |
|:---:|:---|
| `FORCE_COLOR` | Force enable color output |
| `NO_COLOR` | Disable color output |
| `TERM=dumb` | Disable color output |

## Contributing

Contributions are welcome!

1. **Fork** this repository
2. **Add** your node source to `config.json`
3. **Submit** a Pull Request

**Guidelines:**

- ✅ Only add legitimate free node sources
- ✅ Ensure URL is accessible and returns valid nodes before submitting
- ✅ Avoid duplicate sources

## Dependencies

- [requests](https://pypi.org/project/requests/) - HTTP requests
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - HTML parsing

## Disclaimer

1. For learning and research purposes only
2. Free nodes are not guaranteed to be stable, recommended for testing only
3. Please comply with local laws and regulations
4. Verify security of subscription sources yourself

## License

[MIT](LICENSE)
