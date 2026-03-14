
from pprint import pprint
import json
import subprocess
from datetime import datetime
from time import time, sleep
import os
from utility import *
from urllib.parse import quote, unquote
import requests


config = json.load(open("config.json", "r", encoding="utf-8"))

online_query_list = []
try:
    res = requests.get("https://xuc7950.github.io/FreeNodeAggregator/config.json", timeout=10)
    if res != "" and res.status_code == 200:
        online_query_list = json.loads(res.text)["query_list"]
    res.close()
except: pass

print(f"当前系统: {system_type}")
print(f"在线节点（{len(online_query_list)}）：")
pprint(online_query_list)

start_time = time()
update_time = config["update_time"]
update_time = [int(x) for x in update_time.split(":")]
proc = None

while True:
    if proc == None or (datetime.now().hour == update_time[0] and datetime.now().minute == update_time[1]):
        if proc != None:
            proc.terminate()
            round += 1
            print("----------------------------------------------------------------------------------")
            print(f"您的服务已稳定运行{(time()-start_time)/3600:.2f}小时，正在更新节点...")
            print(f"当前更新轮次为：{round}")
            print("注意：更新过程中可能会短暂无法访问订阅链接，请更新完成后刷新。建议更新时间设置为每天凌晨。")
        else:
            round = 1
            print("当前开始时间为：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print("开始第一次获取节点...")
        all_nodes = []
        count = 0
        query_list = config["query_list"]
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
                if line.startswith("vmess://") and line.find("#") == -1:
                    download = float(all_items[7]) / 8.192
                    uoload = float(all_items[8]) / 8.192
                    delay = float(all_items[5])
                    is_valid = all_items[1]=="passed" and download > config["test"]["speed_threshold"]
                    if (is_valid):
                        proto = link[:link.find("://")+3]
                        content = link.replace(proto, "")
                        content = base64.b64decode(content).decode('utf-8')
                        content = json.loads(content)
                        content["ps"] += f" | 延迟: {delay}ms | 下载: {download:.2f}Mb/s | 上传: {uoload:.2f}Mb/s"
                        all_nodes.append(proto + base64.b64encode(json.dumps(content, ensure_ascii=False).encode('utf-8')).decode('utf-8'))
                elif line.startswith("ss://") or line.startswith("ssr://") or line.startswith("trojan://") or line.startswith("vless://"):
                    download = float(all_items[7]) / 8.192
                    uoload = float(all_items[8]) / 8.192
                    delay = float(all_items[5])
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

        if (len(online_query_list) != 0 and len(online_query_list) < len(config["query_list"])):
            print_contribution_box()

        proc = subprocess.Popen([["python3","python"][system_type=="Windows"], "-m", "http.server", str(config["port"])])
    sleep(59)