
import requests
from bs4 import BeautifulSoup
import base64
import re
from pprint import pprint
import os
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def get_nodes_by_two_steps(url, match1, match2, timeout=10):
    print(f"\n-----开始获取节点--{url}---------")
    new_url = ""
    all_nodes = []
    space = "  "
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        print(f"{space}状态码: {response.status_code}")
        print(f"{space}内容长度: {len(response.text)} 字符")
        
        if response.status_code == 200:
            print(space+"请求成功！")
            soup = BeautifulSoup(response.text, 'html.parser')
            new_url = soup.select(match1)[0].get("href")
            if not new_url.startswith("http"):
                new_url = url + new_url
        else:
            print(f"{space}请求失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{space}请求异常: {e}")
    if (new_url != ""):
        try:
            response = requests.get(new_url, headers=headers, timeout=timeout)
            print(f"{space}新url状态码: {response.status_code}")
            print(f"{space}新url内容长度: {len(response.text)} 字符")
            
            if response.status_code == 200:
                print(space+"新url请求成功！")
                soup = BeautifulSoup(response.text, 'html.parser')
                all_node_els = soup.select(match2)
                for el in all_node_els:
                    link_text = re.sub(r'\s+', '', el.getText())
                    if link_text.endswith(".txt"):
                        all_nodes.append(link_text)
            else:
                print(f"{space}新url请求失败，状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"{space}新url请求异常: {e}")
        print(all_nodes)
    print("-----获取节点结束------------------------")
    return all_nodes

def quick_download_merge(urls, output='merged.txt'):
    """
    快速下载合并版本
    """
    all_links = set()
    
    print("开始下载订阅...")
    
    for url in urls:
        print(f"\n下载: {url}")
        
        try:
            # 下载
            r = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            content = r.text.strip()
            
            # 尝试Base64解码
            try:
                clean = content.replace('\n', '').replace(' ', '')
                clean += '=' * (-len(clean) % 4)
                content = base64.b64decode(clean).decode('utf-8')
            except:
                pass
            
            # 提取链接
            links = []
            for line in content.split('\n'):
                line = line.strip()
                if re.match(r'^(vmess|ss|ssr|trojan|vless)://', line, re.I):
                    links.append(line)
            
            if links:
                before = len(all_links)
                all_links.update(links)
                after = len(all_links)
                print(f"✓ 找到 {len(links)} 个链接，新增 {after-before} 个")
            else:
                print("✗ 未找到有效链接")
                
        except Exception as e:
            print(f"✗ 下载失败: {e}")
    
    # 合并保存
    if all_links:
        links_list = list(all_links)
        plain = '\n'.join(links_list)
        encoded = base64.b64encode(plain.encode()).decode()
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        print(f"\n✅ 合并完成！")
        print(f"📊 总节点数: {len(links_list)}")
        print(f"💾 文件: {output}")
        
        # 显示订阅内容
        print(f"\n📋 订阅内容（可复制导入）:")
        print(encoded[:300] + "...")
        print(f"订阅链接1：http://127.0.0.1:8000/free_nodes_merged.txt")
        print(f"订阅链接2：http://{get_local_ip()}:8000/free_nodes_merged.txt")
        print()
        
        return output
    else:
        print("\n❌ 未获取到任何节点")
        return None

query_list = [
    {"url": "https://nodefree.me", "match1": "article a", "match2": ".section p"},
    {"url": "https://www.freev2raynode.com", "match1": ".col-md-3 a", "match2": ".post-content-content p"},
    {"url": "https://www.freeclashnode.com", "match1": ".col-md-3 a", "match2": ".post-content-content p"},
    {"url": "https://clashfreenode.com", "match1": ".list-body a", "match2": ".subCopy"},
    {"url": "https://freenodes.net", "match1": ".col-md-3 a", "match2": ".post-content-content p"},
    {"url": "https://oneclash.cc", "match1": ".post_def_left", "match2": ".wznrys p"},
    {"url": "https://shadowsocksr.org", "match1": ".col-md-3 a", "match2": ".post-content-content p"}
]

all_nodes = []
count = 0
for query in query_list:
    print(f"\n正在获取第{count+1}/{len(query_list)}个网址节点：{query['url']}")
    all_nodes += get_nodes_by_two_steps(query["url"], query["match1"], query["match2"])
    count += 1
pprint(all_nodes)

result = quick_download_merge(all_nodes, 'free_nodes_merged.txt')
os.system("python -m http.server")