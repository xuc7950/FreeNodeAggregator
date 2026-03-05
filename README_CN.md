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

## 项目结构

```
.
├── main.py              # 主程序
├── config.json          # 订阅源配置文件
├── requirements.txt     # Python 依赖
├── run.bat              # Windows 启动脚本
├── run.sh               # Linux/Mac 启动脚本
└── free_nodes_merged.txt # 合并后的订阅文件（运行后生成）
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

程序运行后会：
1. 从 `config.json` 中配置的所有源获取节点
2. 合并并去重所有节点
3. 生成 `free_nodes_merged.txt` 文件
4. 启动本地 HTTP 服务器
5. 持续运行，在设定时间自动更新节点

### 导入订阅

运行后，可使用以下地址导入客户端：

- 本地：`http://127.0.0.1:<端口>/free_nodes_merged.txt`
- 局域网：`http://<你的IP>:<端口>/free_nodes_merged.txt`

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
    "update_time": [0, 0],
    "port": 2352
}
```

### 全局参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `query_list` | 数组 | 节点来源列表 |
| `update_time` | 数组 | 每日更新时间 `[小时, 分钟]`，如 `[0, 0]` 表示凌晨 |
| `port` | 数字 | HTTP 服务器端口（默认：2352） |

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
    "update_time": [0, 0],
    "port": 2352
}
```

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
