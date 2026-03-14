import platform
import requests
from bs4 import BeautifulSoup
import base64
import re
import socket
from pprint import pprint

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
system_type = ""
if platform.system() == "Windows":
    system_type = "Windows"
elif platform.system() == "Linux":
    system_type = "Linux"
elif platform.system() == "Darwin":
    system_type = "MacOS"
else:
    system_type = "Unknown"

# 颜色代码
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

def get_display_width(text):
    """计算字符串的显示宽度（考虑中文和宽字符）"""
    # 移除ANSI颜色代码
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    clean_text = ansi_escape.sub('', text)

    width = 0
    for char in clean_text:
        code = ord(char)
        # 中文、全角字符、emoji等宽字符
        if code > 0x7F:
            width += 2
        else:
            width += 1
    return width

def print_cool_box(text, icon="🚀"):
    """打印一个炸裂酷炫的边框框"""
    lines = [line for line in text.split('\n') if line.strip()]


    # 计算内容区域宽度（基于最长行的显示宽度）
    max_content_width = max(get_display_width(line) for line in lines)
    # 内部宽度 = 内容宽度 + 前缀emoji宽度(2) + 额外间距
    inner_width = max_content_width + 6

    # 打印顶部装饰线
    top_line = '═' * (inner_width + 4)
    print(f"\n{CYAN}{BOLD}{top_line}{RESET}")

    # 打印顶部边框
    print(f"{CYAN}{BOLD}╔{'═' * inner_width}╗{RESET}")

    # 标题行
    title = "代理节点订阅服务"
    title_display = get_display_width(title)
    icon_display = get_display_width(icon)
    # 计算标题行需要的空格
    title_content_width = icon_display + 2 + title_display + 2  # icon + 空格 + 标题 + 右边距
    title_padding = inner_width - title_content_width
    print(f"{MAGENTA}║{RESET} {GREEN}{icon}{RESET} {CYAN}【{title}】{RESET}{' ' * title_padding}{MAGENTA}║{RESET}")

    # 分割线
    print(f"{YELLOW}╠{'─' * inner_width}╣{RESET}")

    # 打印内容行
    for line in lines:
        # 根据内容选择emoji
        if "订阅链接" in line:
            emoji = "🔗"
            emoji_color = BLUE
        elif "节点总数" in line:
            emoji = "📊"
            emoji_color = GREEN
        elif "更新轮次" in line:
            emoji = "🔄"
            emoji_color = MAGENTA
        elif "更新时间" in line:
            emoji = "🕐"
            emoji_color = CYAN
        elif "测试模式" in line:
            emoji = "⚙"
            emoji_color = YELLOW
        elif "测试线程数" in line:
            emoji = "🚀"
            emoji_color = RED
        else:
            emoji = "•"
            emoji_color = WHITE

        # 计算这行需要的填充
        line_display = get_display_width(line)
        padding = inner_width - line_display - 4  # 减去emoji(2)和间距(2)

        # 打印行
        print(f"{MAGENTA}║{RESET} {emoji_color}{emoji}{RESET} {YELLOW}{BOLD}{line}{RESET}{' ' * padding}{MAGENTA}║{RESET}")

    # 分割线
    print(f"{YELLOW}╠{'─' * inner_width}╣{RESET}")

    # 底部装饰
    stars = "★ ✦ ✧ ★ ✦ ✧ ★ ✦ ✧"
    stars_display = get_display_width(stars)
    stars_padding = inner_width - stars_display - 2
    print(f"{MAGENTA}║{RESET} {GREEN}{stars}{' ' * stars_padding}{MAGENTA}║{RESET}")

    # 打印底部边框
    print(f"{CYAN}{BOLD}╚{'═' * inner_width}╝{RESET}")

    # 打印底部装饰线
    print(f"{CYAN}{BOLD}{top_line}{RESET}\n")

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

def get_nodes_directly(url, timeout=10):
    print(f"\n-----开始获取节点--{url}---------")
    all_nodes = ""
    space = "  "
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        print(f"{space}状态码: {response.status_code}")
        print(f"{space}内容长度: {len(response.text)} 字符")
        
        if response.status_code == 200:
            all_nodes = response.text.strip()
        else:
            print(f"{space}请求失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{space}请求异常: {e}")
    print("-----获取节点结束------------------------")
    return all_nodes
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
            print(space+GREEN+"请求成功！"+RESET)
            soup = BeautifulSoup(response.text, 'html.parser')
            new_url = soup.select(match1)[0].get("href")
            if not new_url.startswith("http"):
                new_url = url + new_url
        else:
            print(f"{space}请求失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{space}{RED}请求异常: {e}{RESET}")
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
                pprint(f"{space}新url请求失败，状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"{space}新url请求异常: {e}")
        print(all_nodes)
    print("-----获取节点结束------------------------")
    return all_nodes

def quick_download_merge(all_urls, output='merged.txt') -> int:
    """
    快速下载合并版本
    """
    all_links = set()
    
    print("开始下载订阅...")
    
    for urls in all_urls:
        if type(urls) is str:
            links = []
            content = base64.b64decode(urls).decode('utf-8')
            for line in content.split('\n'):
                line = line.strip()
                if re.match(r'^(vmess|ss|ssr|trojan|vless)://', line, re.I):
                    links.append(line)
            
            if links:
                before = len(all_links)
                all_links.update(links)
                after = len(all_links)
                print(f"{GREEN}✓ 找到 {len(links)} 个链接，新增 {after-before} 个{RESET}")
            else:
                print(f"{RED}✗ 未找到有效链接{RESET}")
            continue

        print(f"\n下载: {urls}")
        for url in urls:
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
                    print(f"{GREEN}✓ 找到 {len(links)} 个链接，新增 {after-before} 个{RESET}")
                else:
                    print(f"{RED}✗ 未找到有效链接{RESET}")
                    
            except Exception as e:
                print(f"{RED}✗ 下载失败: {e}{RESET}")
    
    # 合并保存
    if all_links:
        links_list = list(all_links)
        plain = '\n'.join(links_list)
        encoded = plain.encode().decode()
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(encoded)
        
        print(f"\n✅ 合并完成！")
        print(f"📊 总节点数: {len(links_list)}")
        print(f"💾 文件: {output}")
        
        # 显示订阅内容
        # print(f"\n📋 订阅内容（可复制导入）:")
        # print(encoded[:300] + "...\n")
        
        return len(links_list)
    else:
        print("\n❌ 未获取到任何节点")
        return 0

proxy_pattern = re.compile(
    r'^(?:'
    r'vmess://[A-Za-z0-9+/=]+|'           # VMess
    r'vless://[A-Fa-f0-9-]+@[^:]+:\d+\?[^#\s]+(?:#[^\s]+)?|'  # VLESS
    r'trojan://[^@]+@[^:]+:\d+(?:\?[^#\s]*)?(?:#[^\s]+)?|'     # Trojan
    r'ss://(?:[A-Za-z0-9+/=]+|[A-Za-z0-9_-]+@[^:]+:\d+)(?:#[^\s]+)?'  # Shadowsocks
    r')$'
)

def print_contribution_box():
    """打印贡献节点提示框"""
    inner_width = 64

    # 顶部装饰线
    top_line = '═' * (inner_width + 4)
    print(f"\n{YELLOW}{BOLD}{top_line}{RESET}")

    # 顶部边框
    print(f"{YELLOW}╔{'═' * inner_width}╗{RESET}")

    # 标题行
    title = "开源贡献邀请"
    title_display = get_display_width(title)
    title_padding = (inner_width - title_display - 6) // 2  # 减去icon和空格
    print(f"{YELLOW}║{RESET}{' ' * title_padding}{GREEN}🌟{RESET} {CYAN}【{title}】{RESET}{GREEN}🌟{RESET}{' ' * title_padding}{YELLOW}║{RESET}")

    # 分割线
    print(f"{YELLOW}╠{'─' * inner_width}╣{RESET}")

    # 内容行
    content_lines = [
        ("💡", "检测到您本地的测试节点可能有所更新", BLUE),
        ("🤝", "欢迎为开源项目贡献您的节点资源！", MAGENTA),
        ("", "", WHITE),  # 空行
        ("📦", "项目地址: github.com/xuc7950/FreeNodeAggregator", CYAN),
        ("📧", "联系邮箱: xuc7950@foxmail.com", GREEN),
        ("", "", WHITE),  # 空行
        ("🎓", "贡献教程: B站搜索「如何在github上贡献代码」", YELLOW),
    ]

    for icon, text, color in content_lines:
        if icon == "":  # 空行
            print(f"{YELLOW}║{' ' * inner_width}║{RESET}")
        else:
            line_text = f"{icon} {text}"
            line_display = get_display_width(line_text)
            padding = inner_width - line_display - 2
            print(f"{YELLOW}║{RESET} {color}{line_text}{RESET}{' ' * padding}{YELLOW}║{RESET}")

    # 底部分割线
    print(f"{YELLOW}╠{'─' * inner_width}╣{RESET}")

    # 感谢语
    thanks = "感谢您的支持，让开源社区更美好！"
    thanks_display = get_display_width(thanks)
    thanks_padding = (inner_width - thanks_display - 4) // 2
    print(f"{YELLOW}║{RESET}{' ' * thanks_padding}{GREEN}❤️ {thanks}{RESET}{' ' * thanks_padding}{YELLOW}║{RESET}")

    # 底部边框
    print(f"{YELLOW}╚{'═' * inner_width}╝{RESET}")

    # 底部装饰线
    print(f"{YELLOW}{BOLD}{top_line}{RESET}\n")

def is_proxy_link(link):
    return bool(proxy_pattern.match(link.strip()))