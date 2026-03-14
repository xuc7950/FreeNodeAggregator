# 免费代理节点订阅聚合工具

[English](README.md) | 简体中文

> 本项目配合 [Karing](https://github.com/KaringX/karing) 使用更佳！Karing 是一款跨平台的代理客户端，支持多种协议，界面简洁易用。

一个自动从多个免费节点源获取、合并并去重代理节点的 Python 工具，支持生成统一的订阅链接。

## 功能特点

- **多源聚合**：从多个免费节点订阅源同时获取节点
- **自动去重**：合并时自动去除重复节点
- **多协议支持**：支持 vmess、ss、ssr、trojan、vless 等主流协议
- **Base64 编码**：输出标准 Base64 编码的订阅内容，可直接导入客户端
- **本地服务器**：自动启动 HTTP 服务器，提供本地订阅链接
- **定时更新**：支持每天定时自动刷新节点
- **自定义端口**：HTTP 服务器端口可配置
- **节点测试**：内置节点可用性测试，支持两种模式：
  - **基础模式**：快速连通性测试
  - **完整模式**：完整测速，包含延迟、上传/下载速度指标
- **智能过滤**：根据可配置的速度阈值过滤低速节点

## 项目结构

```
.
├── main.py               # 主程序
├── utility.py            # 工具函数
├── config.json           # 订阅源配置文件
├── requirements.txt      # Python 依赖
├── run.bat               # Windows 启动脚本
├── run.sh                # Linux/Mac 启动脚本
├── tools/                # 节点测试工具
│   ├── Windows/          # Windows xray-knife
│   └── Linux/            # Linux xray-knife
├── free_nodes_raw.txt    # 原始合并节点（运行后生成）
├── free_nodes_filtered.txt # 测试过滤后的节点（运行后生成）
└── free_nodes_filtered.csv # 测试结果CSV（完整模式下生成）
```

## 安装

### 前置要求

- Python 3.6+

### 安装依赖

**Windows:**
```bash
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
pip3 install -r requirements.txt
```

## 使用方法

### 快速启动

**Windows:**
双击运行 `run.bat` 或执行：
```bash
run.bat
```

**Linux/Mac:**
```bash
bash run.sh
```

### 手动运行

```bash
python main.py
```

### 使用自定义配置文件

使用 `--config` 或 `-c` 参数指定自定义配置文件：

```bash
python main.py --config myconfig.json
python main.py -c /path/to/config.json
```

### Docker 部署

**1. 加载 Docker 镜像：**
```bash
sudo docker load -i FreeNodesAggregator@0.0.2-Docker.tar
```

**2. 使用自定义配置启动容器：**
```bash
sudo docker run --name free_node_aggregator \
  -d \
  -p 2352:2352 \
  -v /path/to/your/config.json:/FreeNodeAggregator/config.json \
  free_node_aggregator:0.0.2
```

**参数说明：**
| 参数 | 说明 |
|------|------|
| `-d` | 后台运行（守护模式） |
| `-p 2352:2352` | 将容器端口映射到主机端口 |
| `-v` | 挂载自定义配置文件到容器 |

**3. 查看日志：**
```bash
sudo docker logs -f free_node_aggregator
```

**4. 停止/重启容器：**
```bash
sudo docker stop free_node_aggregator
sudo docker start free_node_aggregator
```

程序运行后会：
1. 从 `config.json` 中配置的所有源获取节点
2. 合并并去重所有节点
3. 测试节点可用性（如果启用了测试功能）
4. 根据测试模式生成输出文件
5. 启动本地 HTTP 服务器
6. 持续运行，在设定时间自动更新节点

### 导入订阅

运行后，可使用以下地址导入客户端：

- 本地：`http://127.0.0.1:<端口>/free_nodes_filtered.txt`（如果禁用测试则使用 `free_nodes_raw.txt`）
- 局域网：`http://<你的IP>:<端口>/free_nodes_filtered.txt`

> 注意：将 `<端口>` 替换为 `config.json` 中配置的端口（默认：2352）

## 配置说明

编辑 `config.json` 配置订阅源和服务器设置。

### 配置文件结构

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

### 全局参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `query_list` | 数组 | 节点来源列表 |
| `update_time` | 字符串 | 每日更新时间，格式为 `HH:MM`，如 `"00:00"` 表示凌晨 |
| `port` | 数字 | HTTP 服务器端口（默认：2352） |
| `test` | 对象 | 节点测试配置 |

### 测试参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `mode` | 字符串 | 测试模式：`"none"`（跳过测试）、`"basic"`（仅连通性测试）、`"full"`（完整测速） |
| `threads` | 数字 | 并发测试线程数（默认：50） |
| `speed_threshold` | 数字 | 最低下载速度阈值，单位 Mb/s，用于过滤节点（完整模式下使用） |

### 模式一：直接订阅链接

适用于直接返回节点内容的 URL（Base64 编码或明文）。

#### 配置示例

```json
{
    "url": "https://raw.githubusercontent.com/free-nodes/v2rayfree/main/v202603022"
}
```

### 模式二：两步获取模式

适用于需要先访问页面再提取订阅链接的网站。

#### 配置示例

```json
{
    "url": "https://example.com",
    "match1": "article a",
    "match2": ".content p"
}
```

#### 参数说明

| 参数 | 说明 |
|------|------|
| `url` | 目标网站 URL |
| `match1` | 在第一个页面中查找订阅链接的 CSS 选择器 |
| `match2` | 在第二个页面中提取节点内容的 CSS 选择器 |

### 完整配置示例

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

## 输出文件

运行后会生成以下文件：

| 文件 | 说明 |
|------|------|
| `free_nodes_raw.txt` | 未经测试的合并节点 |
| `free_nodes_filtered.txt` | 测试过滤后的节点（basic/full 模式） |
| `free_nodes_filtered.csv` | 详细测试结果CSV（仅 full 模式） |

## 欢迎贡献

欢迎大家贡献节点 URL！🎉

本项目的节点库依赖于社区的贡献才能不断壮大。如果你知道任何免费的代理节点来源，欢迎通过以下方式贡献：

1. **Fork** 本仓库
2. **添加** 你的节点源到 `config.json`
3. **提交** Pull Request

你的贡献会让这个工具对每个人都有帮助。让我们一起构建更好的节点池！

### 贡献指南

- 只添加**合法**的免费节点来源
- 提交前测试 URL（确保返回有效的代理链接）
- 清晰提供来源网站 URL
- 避免添加配置中已存在的重复来源

## 依赖

- `requests` - HTTP 请求
- `beautifulsoup4` - HTML 解析

## 注意事项

1. 本工具仅供学习研究使用
2. 免费节点稳定性不保证，建议仅用于测试
3. 请遵守当地法律法规，合法使用网络资源
4. 订阅源来自公开网络，请自行甄别安全性

## 许可证

MIT
