
from pprint import pprint
import json
import csv
import subprocess
from datetime import datetime
from time import time, sleep
import os
import argparse
from utility import *
from urllib.parse import quote, unquote, urlsplit, urlunsplit, parse_qsl, urlencode
import requests
from server import start_server


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='免费代理节点订阅聚合工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py                           # 使用默认配置 config.json
  python main.py --config myconfig.json    # 使用自定义配置文件
  python main.py -c /path/to/config.json   # 使用绝对路径配置
        '''
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config.json',
        help='指定配置文件路径 (默认: config.json)'
    )
    return parser.parse_args()

def load_config(config_path):
    """加载配置文件"""
    if not os.path.exists(config_path):
        print(f"{RED}错误: 配置文件不存在: {config_path}{RESET}")
        print(f"{YELLOW}提示: 请确保配置文件存在，或使用 --config 指定正确的路径{RESET}")
        exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"{RED}错误: 配置文件格式错误: {e}{RESET}")
        exit(1)
    except Exception as e:
        print(f"{RED}错误: 无法读取配置文件: {e}{RESET}")
        exit(1)

def repl(m):
    expr = m.group(1)
    return str(eval(expr))
def parse_config(config):
    for i, query in enumerate(config["query_list"]):
        for key, value in query.items():
            config["query_list"][i][key] = re.sub(r"\{(.*?)\}", repl, value)


def get_update_time_parts(config):
    update_time_text = str(config.get("update_time", "03:00"))
    return [int(x) for x in update_time_text.split(":")]


def reload_config_if_changed(config_path, last_mtime, config, update_time, server_port):
    """检测配置文件改动并热刷新运行时配置。"""
    try:
        current_mtime = os.path.getmtime(config_path)
    except OSError:
        return config, update_time, last_mtime

    if last_mtime is not None and current_mtime <= last_mtime:
        return config, update_time, last_mtime

    try:
        new_config = load_config(config_path)
        parse_config(new_config)
        new_update_time = get_update_time_parts(new_config)
    except Exception as e:
        print(f"{YELLOW}检测到配置文件变化，但重载失败：{e}{RESET}")
        return config, update_time, last_mtime

    if int(new_config.get("port", server_port)) != int(server_port):
        print(f"{YELLOW}检测到端口变更为 {new_config.get('port')}，需重启程序后生效（当前仍使用 {server_port}）。{RESET}")

    print(f"{GREEN}检测到配置已更新，已自动重载: {os.path.abspath(config_path)}{RESET}")
    return new_config, new_update_time, current_mtime


def get_test_prefer_by(config):
    """获取 full 测速后的优选排序策略。"""
    aliases = {
        "speed": "download",
        "speedtest": "download",
        "download": "download",
        "upload": "upload",
        "latency": "latency",
        "delay": "latency",
    }
    prefer_by = str(config.get("test", {}).get("prefer_by", "download")).strip().lower()
    if prefer_by not in aliases:
        print(f"{YELLOW}未知优选策略 {prefer_by}，已回退为 download{RESET}")
        return "download"
    return aliases[prefer_by]


def parse_speedtest_number(value):
    """将 xray-knife CSV 中的数值字段转为 float，非法值返回 None。"""
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text == "null":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def sort_speedtest_rows(rows, prefer_by):
    """按优选策略排序测速结果：默认下载速度优先，延迟仅作为兜底排序。"""
    def sort_key(row):
        download = parse_speedtest_number(row.get("download"))
        upload = parse_speedtest_number(row.get("upload"))
        delay = parse_speedtest_number(row.get("delay"))
        status_rank = 0 if row.get("status") == "passed" else 1
        safe_download = download if download is not None else -1
        safe_upload = upload if upload is not None else -1
        safe_delay = delay if delay is not None else float("inf")

        if prefer_by == "latency":
            return (status_rank, safe_delay, -safe_download, -safe_upload)
        if prefer_by == "upload":
            return (status_rank, -safe_upload, -safe_download, safe_delay)
        return (status_rank, -safe_download, -safe_upload, safe_delay)

    return sorted(rows, key=sort_key)


def get_karing_latency_value(prefer_by, delay, preferred_index):
    """生成 Karing 用于自动优选的 latency 参数，数值越小优先级越高。"""
    if prefer_by == "latency":
        return max(1, int(round(delay)))
    return preferred_index + 1


def add_query_param(link, key, value):
    """在标准 URI 中写入查询参数，保留已有 query 和 fragment。"""
    parts = urlsplit(link)
    query_items = [
        (item_key, item_value)
        for item_key, item_value in parse_qsl(parts.query, keep_blank_values=True)
        if item_key != key
    ]
    query_items.append((key, str(value)))
    query = urlencode(query_items)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def add_ssr_query_param(link, key, value):
    """SSR 链接的参数在整体 base64 载荷内，需要解码后再写入。"""
    encoded = link.replace("ssr://", "", 1)
    try:
        padding = "=" * (-len(encoded) % 4)
        decoded = base64.urlsafe_b64decode((encoded + padding).encode()).decode("utf-8")
    except Exception:
        return link

    main_part, separator, query = decoded.partition("/?")
    query_items = [
        (item_key, item_value)
        for item_key, item_value in parse_qsl(query, keep_blank_values=True)
        if item_key != key
    ]
    query_items.append((key, str(value)))
    updated = main_part + separator + urlencode(query_items)
    encoded_updated = base64.urlsafe_b64encode(updated.encode()).decode().rstrip("=")
    return "ssr://" + encoded_updated


def add_karing_latency(link, latency):
    """为 Karing 写入可识别的 latency 参数，用测速排序结果驱动自动优选。"""
    if link.startswith("ssr://"):
        return add_ssr_query_param(link, "latency", latency)
    return add_query_param(link, "latency", latency)


def append_link_note(link, note):
    """将测速说明追加到 URI fragment，避免污染 query 参数。"""
    if link.startswith("ssr://"):
        return link

    parts = urlsplit(link)
    fragment = f"{parts.fragment}{quote(note)}"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, fragment))


# 解析参数并加载配置
args = parse_args()
config = load_config(args.config)
parse_config(config)

print(f"配置文件: {os.path.abspath(args.config)}")
pprint(config)

only_test = False
online_query_list = []
try:
    res = requests.get("https://xuc7950.github.io/FreeNodeAggregator/config.json", timeout=10)
    if res != "" and res.status_code == 200:
        online_query_list = json.loads(res.text)["query_list"]
    res.close()
except: pass

print(f"当前系统: {system_type}")
print(f"终端模式: {'彩色' if COLOR_SUPPORTED else '黑白'} / {'UTF-8' if UTF8_SUPPORTED else 'ASCII'}")
# print(f"线上节点（{len(online_query_list)}）：")
# pprint(online_query_list)

start_time = time()
update_time = get_update_time_parts(config)
is_first_run = True
server_port = int(config["port"])
start_server(port=server_port)
config_mtime = os.path.getmtime(args.config) if os.path.exists(args.config) else None

while True:
    config, update_time, config_mtime = reload_config_if_changed(
        args.config, config_mtime, config, update_time, server_port
    )
    can_loop_test = only_test and datetime.now().minute % config["loop_test_interval"] == 0
    is_update_time = (datetime.now().hour == update_time[0] and datetime.now().minute == update_time[1])
    only_test = not is_update_time
    if not os.path.exists("free_nodes_raw.txt"):
        only_test = False
    if is_first_run or is_update_time or can_loop_test:
        if not is_first_run:
            round += 1
            print("----------------------------------------------------------------------------------")
            print(f"您的服务已稳定运行{(time()-start_time)/3600:.2f}小时，正在更新节点...")
            print(f"当前更新轮次为：{round}")
        else:
            round = 1
            print("当前开始时间为：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print("开始第一次获取节点...")
        all_nodes = []
        all_node_count = 0
        if (only_test):
            with open("free_nodes_raw.txt", "r", encoding="utf-8") as file:
                all_node_count = len(file.readlines())
                for line in file:
                    line = line.strip()
                    if line != "":
                        all_nodes.append(line)
        else:
            query_list = config["query_list"]
            count = 0
            for query in query_list:
                print(f"\n正在获取第{count+1}/{len(query_list)}个网址节点：{query['url']}")
                if "match1" not in query or "match2" not in query:
                    all_nodes.append(get_nodes_directly(query["url"]))
                else:
                    all_nodes.append(get_nodes_by_two_steps(query["url"], query["match1"], query["match2"]))
                count += 1
            for node in all_nodes:
                if (type(node) is list):
                    pprint(node)
                else:
                    print("获取到节点内容，长度:", len(node), "字符")
            all_node_count = quick_download_merge(all_nodes, 'free_nodes_raw.txt')

        node_test_tool = ""
        if system_type == "Windows":
            node_test_tool = f".\\tools\\{system_type}\\xray-knife.exe"
        elif system_type == "Linux":
            node_test_tool = f"./tools/{system_type}/xray-knife"
        elif system_type == "Darwin":
            node_test_tool = f"./tools/MacOS/xray-knife"
        
        # 可用性检测
        if config["test"]["mode"] == "basic":
            os.system(f"{node_test_tool} http -f free_nodes_raw.txt -t {str(config['test']['threads'])} -o free_nodes_filtered.txt")
        elif config["test"]["mode"] == "full":
            os.system(f"{node_test_tool} http -f free_nodes_raw.txt -t {str(config['test']['threads'])} --speedtest --sort=false --type csv -o free_nodes_filtered.csv")
            
            # 将csv中的上传、下载、延迟信息与节点名称拼起来，移除掉下载速度小于阈值的节点，输出到txt文件中
            # 样例数据格式：link	status	reason	tls	ip	delay	code	download	upload	location	ttfb	connect_time
            with open("free_nodes_filtered.csv", "r", encoding="utf-8", newline="") as csv_file:
                speedtest_rows = list(csv.DictReader(csv_file))
            prefer_by = get_test_prefer_by(config)
            speedtest_rows = sort_speedtest_rows(speedtest_rows, prefer_by)
            all_nodes = []
            for row in speedtest_rows:
                link = row.get("link", "")
                download_raw = parse_speedtest_number(row.get("download"))
                upload_raw = parse_speedtest_number(row.get("upload"))
                delay = parse_speedtest_number(row.get("delay"))
                if download_raw is None or upload_raw is None or delay is None:
                    continue
                download = download_raw / 8.192
                upload = upload_raw / 8.192
                if link.startswith("vmess://"):
                    is_valid = row.get("status") == "passed" and download > config["test"]["speed_threshold"]
                    if (is_valid):
                        karing_latency = get_karing_latency_value(prefer_by, delay, len(all_nodes))
                        proto = link[:link.find("://")+3]
                        content = link.replace(proto, "")
                        content = base64.b64decode(content).decode('utf-8')
                        content = json.loads(content)
                        content["ps"] += f" | 延迟: {delay}ms | 下载: {download:.2f}Mb/s | 上传: {upload:.2f}Mb/s"
                        content["latency"] = str(karing_latency)
                        updated_link = proto + base64.b64encode(json.dumps(content, ensure_ascii=False).encode('utf-8')).decode('utf-8')
                        all_nodes.append(updated_link)
                elif link.startswith("ss://") or link.startswith("ssr://") or link.startswith("trojan://") or link.startswith("vless://"):
                    if (download > config["test"]["speed_threshold"]):
                        karing_latency = get_karing_latency_value(prefer_by, delay, len(all_nodes))
                        updated_link = add_karing_latency(link, karing_latency)
                        note = f" | 延迟: {delay}ms | 下载: {download:.2f}Mb/s | 上传：{upload:.2f}Mb/s"
                        all_nodes.append(append_link_note(updated_link, note))

            if len(all_nodes) > 0:
                with open("free_nodes_filtered.txt", "w", encoding="utf-8") as out_file:
                    for node in all_nodes:
                        out_file.write(node + "\n")
            
        output_file_name = ["free_nodes_raw.txt", "free_nodes_filtered.txt"][config["test"]["mode"] == "full" or config["test"]["mode"] == "basic"]
        node_count = len(open(output_file_name, 'r', encoding='utf-8').readlines()) / [1,2][config["test"]["mode"] == "full" or config["test"]["mode"] == "basic"]

        output_text = f"原始订阅链接：http://{get_local_ip()}:{config['port']}/free_nodes_raw.txt\n"
        output_text += f"过滤订阅链接：http://{get_local_ip()}:{config['port']}/{output_file_name}\n"
        output_text += f"滤后节点总数: {len(all_nodes)}/{all_node_count} 个\n"
        if config["test"]["mode"] == "full":
            output_text += f" 过滤阈值：{config['test']['speed_threshold']} Mb/s\n"
            output_text += f" 优选策略：{get_test_prefer_by(config)}\n"
        output_text += f"更新轮次: {round}\n"
        output_text += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output_text += f" 测试模式: {config['test']['mode']}\n"
        output_text += f"测试线程数: {config['test']['threads']}"
        print_cool_box(output_text, "⚡")

        if (len(online_query_list) != 0 and len(online_query_list) != len(config["query_list"])):
            print_contribution_box()
        
        is_first_run = False
        sleep(1)