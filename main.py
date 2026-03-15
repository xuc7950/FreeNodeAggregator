
from pprint import pprint
import json
import subprocess
from datetime import datetime
from time import time, sleep
import os
import argparse
from utility import *
from urllib.parse import quote, unquote
import requests


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
# print(f"在线节点（{len(online_query_list)}）：")
# pprint(online_query_list)

start_time = time()
update_time = config["update_time"]
update_time = [int(x) for x in update_time.split(":")]
proc = None

while True:
    can_loop_test = only_test and datetime.now().minute % config["loop_test_interval"] == 0
    is_update_time = (datetime.now().hour == update_time[0] and datetime.now().minute == update_time[1])
    only_test = not is_update_time
    if not os.path.exists("free_nodes_raw.txt"):
        only_test = False
    if proc == None or is_update_time or can_loop_test:
        if proc != None:
            proc.terminate()
            round += 1
            print("----------------------------------------------------------------------------------")
            print(f"您的服务已稳定运行{(time()-start_time)/3600:.2f}小时，正在更新节点...")
            print(f"当前更新轮次为：{round}")
            print("注意：更新过程中可能会短暂无法访问订阅链接，请更新完成后刷新。建议更新时间设置为每天凌晨，测试时不受影响~")
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
            os.system(f"{node_test_tool} http -f free_nodes_raw.txt -t {str(config['test']['threads'])} --speedtest --sort --type csv -o free_nodes_filtered.csv")
            
            # 将csv中的上传、下载、延迟信息与节点名称拼起来，移除掉下载速度小于阈值的节点，输出到txt文件中
            # 样例数据格式：link	status	reason	tls	ip	delay	code	download	upload	location	ttfb	connect_time
            csv_lines = open("free_nodes_filtered.csv", "r", encoding="utf-8").readlines()
            all_nodes = []
            for line in csv_lines[1:]:
                all_items = line.split(",")
                if all_items[5]=="null" or all_items[7]=="null" or all_items[8]=="null":
                    continue
                link = all_items[0]
                pattern = r'^-?\d*\.?\d+$'
                if not bool(re.match(pattern, str(all_items[7]).strip())) or not bool(re.match(pattern, str(all_items[8]).strip())) or not bool(re.match(pattern, str(all_items[5]).strip())):
                    continue
                download = float(all_items[7]) / 8.192
                uoload = float(all_items[8]) / 8.192
                delay = float(all_items[5])
                if line.startswith("vmess://"):
                    is_valid = all_items[1]=="passed" and download > config["test"]["speed_threshold"]
                    if (is_valid):
                        proto = link[:link.find("://")+3]
                        content = link.replace(proto, "")
                        content = base64.b64decode(content).decode('utf-8')
                        content = json.loads(content)
                        content["ps"] += f" | 延迟: {delay}ms | 下载: {download:.2f}Mb/s | 上传: {uoload:.2f}Mb/s"
                        all_nodes.append(proto + base64.b64encode(json.dumps(content, ensure_ascii=False).encode('utf-8')).decode('utf-8'))
                elif line.startswith("ss://") or line.startswith("ssr://") or line.startswith("trojan://") or line.startswith("vless://"):
                    if (download > config["test"]["speed_threshold"]):
                        all_nodes.append(f"{link}{quote(' | 延迟: ')}{delay}{quote('ms | 下载: ')}{download:.2f}{quote('Mb/s | 上传：')}{uoload:.2f}Mb/s")

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
        output_text += f"更新轮次: {round}\n"
        output_text += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output_text += f" 测试模式: {config['test']['mode']}\n"
        output_text += f"测试线程数: {config['test']['threads']}"
        print_cool_box(output_text, "⚡")

        if (len(online_query_list) != 0 and len(online_query_list) != len(config["query_list"])):
            print_contribution_box()

        proc = subprocess.Popen([["python3","python"][system_type=="Windows"], "-m", "http.server", str(config["port"])])
    sleep(1)