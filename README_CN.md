<div align="center">

# FreeNodeAggregator

**免费代理节点订阅聚合工具**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

一个自动从多个免费节点源获取、合并、测试并去重的代理节点聚合工具。

**[English](README.md)** | 简体中文

</div>

---

## 功能特性

| 特性 | 描述 |
|:---:|:---|
| 🌐 **多源聚合** | 同时从多个免费订阅源获取节点 |
| 🔀 **自动去重** | 合并时智能去除重复节点 |
| 📡 **多协议支持** | 支持 vmess、ss、ssr、trojan、vless 等主流协议 |
| 📦 **标准输出** | 输出 Base64 编码的订阅内容，可直接导入客户端 |
| 🖥️ **内置服务器** | 基于 Flask 的 HTTP 服务器，提供订阅链接 |
| ⏰ **定时更新** | 每天定时自动刷新节点 |
| � **循环测试** | 支持定时重复测试，无需重新获取节点 |
| �� **动态配置** | 支持 Python 表达式动态生成 URL |
| 🧪 **节点测试** | 内置连通性测试与完整测速功能 |
| 🚀 **智能过滤** | 根据速度阈值自动过滤低速节点 |
| 🐳 **Docker 支持** | 完美兼容 Docker 容器部署 |
| � **跨平台支持** | 支持 Windows、Linux、macOS |
| �� **终端适配** | 自动检测终端环境，适配彩色/黑白模式 |

## 快速开始

### 方式一：本地运行

```bash
# 克隆仓库
git clone https://github.com/xuc7950/FreeNodeAggregator.git
cd FreeNodeAggregator

# 安装依赖
pip install -r requirements.txt

# 使用默认配置运行
python main.py
```

<details>
<summary>📖 各平台运行方式</summary>

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

### 方式二：Docker 部署

```bash
# 1) 从 GitHub Release 下载镜像包（示例）
wget https://github.com/xuc7950/FreeNodeAggregator/releases/download/<tag>/free_node_aggregator.tar

# 2) 从 tar 包加载镜像
docker load -i free_node_aggregator.tar

# 3) （可选）检查镜像是否已加载
docker images | grep free_node_aggregator

# 4) 启动容器
docker run --name free_node_aggregator \
  -d \
  -p 2352:2352 \
  -v /path/to/config.json:/FreeNodeAggregator/config.json \
  free_node_aggregator

# 5) 查看日志
docker logs -f free_node_aggregator
```

> 如果你是从源码部署，而不是使用 release 镜像包，请先执行 `docker build -t free_node_aggregator .`。

<details>
<summary>📖 Docker 常用命令</summary>

```bash
# 停止容器
docker stop free_node_aggregator

# 启动容器
docker start free_node_aggregator

# 重启容器
docker restart free_node_aggregator

# 删除容器
docker rm -f free_node_aggregator
```

</details>

## 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|:---:|:---:|:---|:---:|
| `--config` | `-c` | 指定配置文件路径 | `config.json` |

**使用示例：**

```bash
# 使用默认配置
python main.py

# 使用自定义配置文件
python main.py --config myconfig.json
python main.py -c /path/to/config.json

# 查看帮助
python main.py --help
```

## 配置说明

## 通过本地环境变量管理密码

网页配置页面会把密码哈希保存到本地环境变量 `CONFIG_MGR_PASSWORD_HASH` 中。

### 通过终端修改密码（不经过网页）

密码哈希规则：

`sha256(明文密码 + "__config_mgr_salt__")`

可手动生成并更新环境变量：

**Windows（PowerShell）：**

```powershell
$plain = "你的新密码"
$salt = "__config_mgr_salt__"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($plain + $salt)
$hash = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)).Replace("-", "").ToLower()
setx CONFIG_MGR_PASSWORD_HASH $hash
```

> 执行 `setx` 后，建议重开终端（或重启 Python 进程）以确保新会话读取到更新后的环境变量。

**Linux/macOS（bash/zsh）：**

```bash
PLAIN='你的新密码'
HASH=$(python3 -c "import hashlib;print(hashlib.sha256((\"$PLAIN\"+\"__config_mgr_salt__\").encode()).hexdigest())")
echo "export CONFIG_MGR_PASSWORD_HASH='$HASH'" >> ~/.profile
echo "export CONFIG_MGR_PASSWORD_HASH='$HASH'" >> ~/.bashrc
echo "export CONFIG_MGR_PASSWORD_HASH='$HASH'" >> ~/.zshrc
```

然后执行：

```bash
source ~/.profile 2>/dev/null || true
source ~/.bashrc 2>/dev/null || true
source ~/.zshrc 2>/dev/null || true
```

### 检查当前密码哈希是否存在

**Windows（PowerShell）：**

```powershell
[Environment]::GetEnvironmentVariable("CONFIG_MGR_PASSWORD_HASH", "User")
```

**Linux/macOS：**

```bash
echo "$CONFIG_MGR_PASSWORD_HASH"
```

### 配置文件结构

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

### 全局参数

| 参数 | 类型 | 说明 | 默认值 |
|:---|:---:|:---|:---:|
| `update_time` | string | 每日更新时间，格式 `HH:MM` | `"03:00"` |
| `port` | number | HTTP 服务器端口 | `2352` |
| `loop_test_interval` | number | 循环测试间隔（分钟） | `5` |
| `test` | object | 节点测试配置 | - |
| `query_list` | array | 节点来源列表 | `[]` |

### 测试参数

| 参数 | 类型 | 说明 |
|:---|:---:|:---|
| `mode` | string | `none` / `basic` / `full` |
| `threads` | number | 并发测试线程数（建议 10-100） |
| `speed_threshold` | number | 最低速度阈值 Mb/s（仅 `full` 模式生效） |
| `prefer_by` | string | 优选排序依据：`download` / `upload` / `latency`（仅 `full` 模式生效，默认 `download`） |

**测试模式说明：**

| 模式 | 说明 |
|:---:|:---|
| `none` | 跳过测试，直接输出原始节点 |
| `basic` | 连通性测试，仅检测节点可用性 |
| `full` | 完整测速，包含延迟、上传/下载速度，并自动过滤低速节点 |

`full` 模式会先完成测速，再按 `prefer_by` 对过滤后的订阅节点排序。默认使用 `download`，即以测速后的下载速度作为优选依据，而不是使用延迟排序。输出订阅会同时写入 Karing 可识别的 `latency` 参数：速度优选时按测速名次写入更小的数值，让 Karing 自动选择测速结果更好的节点；延迟优选时写入真实延迟值。

### 节点源配置

**模式一：直接订阅链接**

适用于直接返回节点内容的 URL：

```json
{"url": "https://example.com/nodes.txt"}
```

**模式二：两步获取模式**

适用于需要先访问页面再提取订阅链接的网站：

```json
{
    "url": "https://example.com",
    "match1": "article a",
    "match2": ".content p"
}
```

| 参数 | 说明 |
|:---:|:---|
| `url` | 目标网站 URL |
| `match1` | CSS 选择器，用于在首页查找订阅链接 |
| `match2` | CSS 选择器，用于在次页提取节点内容 |

**模式三：动态 URL**

支持在 URL 中嵌入 Python 表达式，使用 `{表达式}` 语法：

```json
{"url": "https://example.com/nodes_{datetime.now().strftime('%Y%m%d')}.txt"}
```

### 完整配置示例

```json
{
    "update_time": "03:00",
    "port": 2352,
    "loop_test_interval": 5,
    "test": {
        "mode": "full",
        "threads": 100,
        "speed_threshold": 0.2,
        "prefer_by": "download"
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

## 输出文件

| 文件 | 说明 |
|:---|:---|
| `free_nodes_raw.txt` | 原始合并节点（未测试） |
| `free_nodes_filtered.txt` | 测试过滤后的可用节点 |
| `free_nodes_speed_preferred.txt` | 网速优选后的可用节点，固定按下载测速结果写入 Karing `latency` 名次（仅 `full` 模式） |
| `free_nodes_filtered.csv` | 详细测速结果（仅 `full` 模式） |

## 订阅地址

程序运行后，可通过以下地址导入客户端：

| 类型 | 地址 |
|:---:|:---|
| 本地 | `http://127.0.0.1:2352/free_nodes_filtered.txt` |
| 局域网 | `http://<你的IP>:2352/free_nodes_filtered.txt` |

如需在 Karing 中按测速网速优选，可导入 `http://<你的IP>:2352/free_nodes_speed_preferred.txt`。

> 💡 **提示**：推荐配合 [Karing](https://github.com/KaringX/karing) 使用，一款跨平台的代理客户端，界面简洁易用。

## 项目结构

```
FreeNodeAggregator/
├── main.py               # 主程序入口
├── utility.py            # 工具函数库
├── server.py             # Flask HTTP 服务器
├── config.json           # 配置文件
├── requirements.txt      # Python 依赖
├── run.bat               # Windows 启动脚本
├── Dockerfile            # Docker 构建文件
├── tools/                # 节点测试工具
│   ├── Windows/          # Windows xray-knife
│   ├── Linux/            # Linux xray-knife
│   └── MacOS/            # macOS xray-knife
└── README.md             # 项目文档
```

## 依赖项

- [requests](https://pypi.org/project/requests/) - HTTP 请求库
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - HTML 解析库
- [flask](https://pypi.org/project/flask/) - Web 服务器框架

## 致谢

本项目使用了以下开源项目：

- **[xray-knife](https://github.com/lilendian0x00/xray-knife)** - 一个强大的 Xray 核心封装工具，用于节点测试和测速。感谢作者提供如此优秀的工具！

## 免责声明

1. 本工具仅供学习研究使用
2. 免费节点稳定性不保证，建议仅用于测试
3. 请遵守当地法律法规，合法使用网络资源
4. 订阅源来自公开网络，请自行甄别安全性

## 许可证

本项目基于 [MIT](LICENSE) 许可证开源。
