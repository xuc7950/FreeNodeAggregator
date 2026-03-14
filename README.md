# Free Proxy Node Subscription Aggregator

English | [简体中文](README_CN.md)

> This project works best with [Karing](https://github.com/KaringX/karing)! Karing is a cross-platform proxy client that supports multiple protocols with a clean and intuitive interface.

A Python tool that automatically fetches, merges, and deduplicates proxy nodes from multiple free sources, generating a unified subscription link.

## Features

- **Multi-source Aggregation**: Fetch nodes from multiple free subscription sources simultaneously
- **Auto Deduplication**: Automatically remove duplicate nodes during merging
- **Multi-protocol Support**: Support vmess, ss, ssr, trojan, vless and other mainstream protocols
- **Base64 Encoding**: Output standard Base64 encoded subscription content, ready to import into clients
- **Local Server**: Automatically start HTTP server providing local subscription links
- **Scheduled Updates**: Automatically refresh nodes at a specified time daily
- **Custom Port**: Configurable HTTP server port
- **Node Testing**: Built-in node availability testing with two modes:
  - **Basic Mode**: Quick connectivity test
  - **Full Mode**: Comprehensive speed test with latency, download/upload speed metrics
- **Smart Filtering**: Filter out low-speed nodes based on configurable speed threshold

## Project Structure

```
.
├── main.py               # Main program
├── utility.py            # Utility functions
├── config.json           # Subscription source configuration
├── requirements.txt      # Python dependencies
├── run.bat               # Windows startup script
├── run.sh                # Linux/Mac startup script
├── tools/                # Node testing tools
│   ├── Windows/          # Windows xray-knife
│   └── Linux/            # Linux xray-knife
├── free_nodes_raw.txt    # Raw merged nodes (generated after running)
├── free_nodes_filtered.txt # Filtered nodes after testing (generated after running)
└── free_nodes_filtered.csv # Test results CSV (generated in full mode)
```

## Installation

### Requirements

- Python 3.6+

### Install Dependencies

**Windows:**
```bash
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
pip3 install -r requirements.txt
```

## Usage

### Quick Start

**Windows:**
Double-click `run.bat` or execute:
```bash
run.bat
```

**Linux/Mac:**
```bash
bash run.sh
```

### Manual Run

```bash
python main.py
```

### Custom Config File

Use `--config` or `-c` to specify a custom configuration file:

```bash
python main.py --config myconfig.json
python main.py -c /path/to/config.json
```

### Docker Deployment

**1. Load Docker Image:**
```bash
sudo docker load -i FreeNodesAggregator@0.0.2-Docker.tar
```

**2. Run Container with Custom Config:**
```bash
sudo docker run --name free_node_aggregator \
  -d \
  -p 2352:2352 \
  -v /path/to/your/config.json:/FreeNodeAggregator/config.json \
  free_node_aggregator:0.0.2
```

**Parameter Explanation:**
| Parameter | Description |
|-----------|-------------|
| `-d` | Run in background (detached mode) |
| `-p 2352:2352` | Map container port to host port |
| `-v` | Mount custom config file to container |

**3. View Logs:**
```bash
sudo docker logs -f free_node_aggregator
```

**4. Stop/Restart Container:**
```bash
sudo docker stop free_node_aggregator
sudo docker start free_node_aggregator
```

The program will:
1. Fetch nodes from all sources configured in `config.json`
2. Merge and deduplicate all nodes
3. Test node availability (if testing is enabled)
4. Generate output files based on testing mode
5. Start a local HTTP server
6. Keep running and automatically update nodes at the scheduled time

### Import Subscription

After running, use the following addresses to import into your client:

- Local: `http://127.0.0.1:<port>/free_nodes_filtered.txt` (or `free_nodes_raw.txt` if testing is disabled)
- LAN: `http://<your_IP>:<port>/free_nodes_filtered.txt`

> Note: Replace `<port>` with the port configured in `config.json` (default: 2352)

## Configuration

Edit `config.json` to configure subscription sources and server settings.

### Config File Structure

```json
{
    "query_list": [
        {
            "url": "https://example.com/subscribe"
        }
    ],
    "update_time": "00:00",
    "port": 2352,
    "test": {
        "mode": "full",
        "threads": 50,
        "speed_threshold": 0.2
    }
}
```

### Global Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query_list` | Array | List of node sources |
| `update_time` | String | Daily update time in `HH:MM` format, e.g. `"00:00"` for midnight |
| `port` | Number | HTTP server port (default: 2352) |
| `test` | Object | Node testing configuration |

### Test Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `mode` | String | Testing mode: `"none"` (skip testing), `"basic"` (connectivity test only), `"full"` (speed test with metrics) |
| `threads` | Number | Number of concurrent test threads (default: 50) |
| `speed_threshold` | Number | Minimum download speed threshold in Mb/s for filtering nodes (used in full mode) |

### Mode 1: Direct Subscription URL

For URLs that return node content directly (Base64 encoded or plain text).

#### Example

```json
{
    "url": "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v202603022"
}
```

### Mode 2: Two-step Fetch Mode

For websites that require visiting a page first, then extracting the subscription link.

#### Example

```json
{
    "url": "https://example.com",
    "match1": "article a",
    "match2": ".content p"
}
```

#### Parameters

| Parameter | Description |
|-----------|-------------|
| `url` | The target website URL |
| `match1` | CSS selector to find the subscription link in the first page |
| `match2` | CSS selector to extract node content from the second page |

### Complete Example

```json
{
    "query_list": [
        {
            "url": "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v202603022"
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
    ],
    "update_time": "00:00",
    "port": 2352,
    "test": {
        "mode": "full",
        "threads": 50,
        "speed_threshold": 0.2
    }
}
```

## Output Files

After running, the following files will be generated:

| File | Description |
|------|-------------|
| `free_nodes_raw.txt` | Merged nodes without testing |
| `free_nodes_filtered.txt` | Filtered nodes after testing (basic/full mode) |
| `free_nodes_filtered.csv` | Detailed test results in CSV format (full mode only) |

## Contributing

Welcome to contribute node URLs! 🎉

This project relies on community contributions to keep growing the available nodes. If you know of any free proxy node sources, please contribute by:

1. **Fork** this repository
2. **Add** your node source to `config.json`
3. **Submit** a Pull Request

Your contribution helps make this tool more useful for everyone. Together we can build a better node pool!

### Contribution Guidelines

- Only add **legitimate** free node sources
- Test the URL before submitting (ensure it returns valid proxy links)
- Provide the source website URL clearly
- Avoid duplicate sources that already exist in the config

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

## Disclaimer

1. This tool is for learning and research purposes only
2. Free nodes are not guaranteed to be stable, recommended for testing only
3. Please comply with local laws and regulations, use network resources legally
4. Subscription sources are from public networks, please verify security yourself

## License

MIT
