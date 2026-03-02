# 免费代理节点订阅聚合工具

[English](README.md) | 简体中文

一个自动从多个免费节点源获取、合并并去重代理节点的 Python 工具，支持生成统一的订阅链接。

## 功能特点

- **多源聚合**：从多个免费节点订阅源同时获取节点
- **自动去重**：合并时自动去除重复节点
- **多协议支持**：支持 vmess、ss、ssr、trojan、vless 等主流协议
- **Base64 编码**：输出标准 Base64 编码的订阅内容，可直接导入客户端
- **本地服务器**：自动启动 HTTP 服务器，提供本地订阅链接

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
4. 启动本地 HTTP 服务器（端口 8000）

### 导入订阅

运行后，可使用以下地址导入客户端：

- 本地：`http://127.0.0.1:8000/free_nodes_merged.txt`
- 局域网：`http://<你的IP>:8000/free_nodes_merged.txt`

## 配置说明

编辑 `config.json` 添加或修改订阅源：

### 直接订阅链接

适用于直接返回节点内容的 URL：

```json
{
    "url": "https://example.com/subscribe"
}
```

### 两步获取模式

适用于需要先访问页面再提取节点的网站：

```json
{
    "url": "https://example.com",
    "match1": "article a",
    "match2": ".content p"
}
```

- `match1`：第一步页面中的链接选择器
- `match2`：第二步页面中节点内容的选择器

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
