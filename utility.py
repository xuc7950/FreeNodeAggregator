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
system_type = platform.system()
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

def supports_color():
    """检测终端是否支持颜色和Unicode"""
    import sys
    import os

    # 检测是否在 Docker 容器中
    in_docker = os.path.exists('/.dockerenv') or os.path.exists('/run/.containerenv')

    # 检测 stdout 是否是 TTY
    is_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    # 检测环境变量
    no_color = os.environ.get('NO_COLOR') or os.environ.get('TERM') == 'dumb'
    force_color = os.environ.get('FORCE_COLOR') or os.environ.get('COLORTERM')

    # 检测是否支持 UTF-8
    try:
        encoding = sys.stdout.encoding or ''
        supports_utf8 = 'utf' in encoding.lower()
    except:
        supports_utf8 = False

    # 强制颜色模式
    if force_color:
        return True, supports_utf8

    # 无颜色模式
    if no_color:
        return False, supports_utf8

    # Docker 环境且非 TTY，默认不使用颜色
    if in_docker and not is_tty:
        return False, supports_utf8

    # 非 TTY 环境（如重定向到文件），不使用颜色
    if not is_tty:
        return False, supports_utf8

    return True, supports_utf8

# 全局颜色支持状态（公开变量，可被 import * 导入）
COLOR_SUPPORTED, UTF8_SUPPORTED = supports_color()

def safe_print(text, fallback=""):
    """安全打印，自动处理编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(fallback if fallback else text.encode('ascii', 'replace').decode('ascii'))

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

def print_cool_box(text, icon="*"):
    """打印一个炸裂酷炫的边框框（兼容Docker环境）"""
    use_color = COLOR_SUPPORTED
    use_utf8 = UTF8_SUPPORTED

    # 根据环境选择边框字符
    if use_utf8:
        h_line = '═'
        h_div = '─'
        tl, tr, bl, br = '╔', '╗', '╚', '╝'
        dl, dr = '╠', '╣'
    else:
        h_line = '='
        h_div = '-'
        tl, tr, bl, br = '+', '+', '+', '+'
        dl, dr = '+', '+'

    lines = [line for line in text.split('\n') if line.strip()]

    # 计算内容区域宽度（基于最长行的显示宽度）
    max_content_width = max(get_display_width(line) for line in lines)
    inner_width = max_content_width + 6

    # 颜色辅助函数
    def c(text, color):
        return f"{color}{text}{RESET}" if use_color else text

    # 打印顶部装饰线
    top_line = h_line * (inner_width + 4)
    print(f"\n{c(top_line, CYAN)}")

    # 打印顶部边框
    print(f"{c(tl + h_line * inner_width + tr, CYAN)}")

    # 标题行
    title = "代理节点订阅服务"
    title_display = get_display_width(title)
    icon_display = get_display_width(icon) if use_utf8 else 1
    title_content_width = icon_display + 2 + title_display + 2
    title_padding = inner_width - title_content_width
    border = '║' if use_utf8 else '|'
    if use_utf8:
        print(f"{c('║', MAGENTA)} {c(icon, GREEN)} {c('【' + title + '】', CYAN)}{' ' * title_padding}{c('║', MAGENTA)}")
    else:
        print(f"{c('|', MAGENTA)} {c(icon, GREEN)} {c('[' + title + ']', CYAN)}{' ' * title_padding}{c('|', MAGENTA)}")

    # 分割线
    print(f"{c(dl + h_div * inner_width + dr, YELLOW)}")

    # emoji 映射（兼容模式使用 ASCII 替代）
    emoji_map = {
        "订阅链接": ("🔗", ">") if use_utf8 else (">", ">"),
        "节点总数": ("📊", "#") if use_utf8 else ("#", "#"),
        "更新轮次": ("🔄", "@") if use_utf8 else ("@", "@"),
        "更新时间": ("🕐", "T") if use_utf8 else ("T", "T"),
        "测试模式": ("⚙", "M") if use_utf8 else ("M", "M"),
        "测试线程数": ("🚀", "X") if use_utf8 else ("X", "X"),
        "过滤阈值": ("📉", "F") if use_utf8 else ("F", "F"),
    }

    # 打印内容行
    for line in lines:
        # 根据内容选择emoji
        emoji = None
        emoji_color = WHITE
        for key, (u8, asc) in emoji_map.items():
            if key in line:
                emoji = u8 if use_utf8 else asc
                if "订阅链接" in key:
                    emoji_color = BLUE
                elif "节点总数" in key:
                    emoji_color = GREEN
                elif "更新轮次" in key:
                    emoji_color = MAGENTA
                elif "更新时间" in key:
                    emoji_color = CYAN
                elif "测试模式" in key or "过滤阈值" in key:
                    emoji_color = YELLOW
                elif "测试线程数" in key:
                    emoji_color = RED
                break

        if emoji is None:
            emoji = "*" if not use_utf8 else "•"

        # 计算这行需要的填充
        line_display = get_display_width(line)
        emoji_display = get_display_width(emoji) if use_utf8 else 1
        padding = inner_width - line_display - emoji_display - 2

        # 打印行
        print(f"{c(border, MAGENTA)} {c(emoji, emoji_color)} {c(line, YELLOW)}{' ' * padding}{c(border, MAGENTA)}")

    # 分割线
    print(f"{c(dl + h_div * inner_width + dr, YELLOW)}")

    # 底部装饰
    if use_utf8:
        stars = "★ ✦ ✧ ★ ✦ ✧ ★ ✦ ✧"
    else:
        stars = "* * * * * * * * * *"
    stars_display = get_display_width(stars)
    stars_padding = inner_width - stars_display - 2
    print(f"{c(border, MAGENTA)} {c(stars, GREEN)}{' ' * stars_padding}{c(border, MAGENTA)}")

    # 打印底部边框
    print(f"{c(bl + h_line * inner_width + br, CYAN)}")

    # 打印底部装饰线
    print(f"{c(top_line, CYAN)}\n")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        s.close()
        return host_ip
    except Exception as e:
        print(f"获取IP失败: {e}")
        return "127.0.0.1"
class NodeExtractor:
    NODE_PREFIXES = ("vmess://", "vless://", "ss://", "trojan://")

    def __init__(self):
        pass

    def _try_b64_decode(self, s: str):
        s = s.strip()
        if not s:
            return None
        try:
            padding = 4 - (len(s) % 4)
            if padding and padding < 4:
                s += "=" * padding
            data = base64.b64decode(s, validate=False)
            return data.decode(errors="ignore")
        except Exception:
            return None

    def _extract_from_line(self, line: str):
        res = []
        stripped = line.strip()
        if any(stripped.startswith(p) for p in self.NODE_PREFIXES):
            res.append(stripped)
            return res

        for token in line.split():
            for p in self.NODE_PREFIXES:
                if p in token:
                    idx = token.index(p)
                    res.append(token[idx:])
                    break
        return res

    def extract_and_encode(self, text: str) -> str:
        """
        输入：原始订阅文本（可能是 markdown、纯 base64、混合）
        输出：所有节点按行拼接后整体 base64 编码的字符串
        """
        decoded = self._try_b64_decode(text)
        if decoded and any(p in decoded for p in self.NODE_PREFIXES):
            work_text = decoded
        else:
            work_text = text

        nodes = []

        for line in work_text.splitlines():
            line = line.strip()
            if not line:
                continue

            inner_decoded = self._try_b64_decode(line)
            if inner_decoded and any(p in inner_decoded for p in self.NODE_PREFIXES):
                for inner_line in inner_decoded.splitlines():
                    nodes.extend(self._extract_from_line(inner_line))
                continue

            nodes.extend(self._extract_from_line(line))

        nodes = [n.strip() for n in nodes if n.strip()]
        nodes = list(dict.fromkeys(nodes))  # 去重并保持顺序

        if not nodes:
            return ""

        joined = "\n".join(nodes)
        return base64.b64encode(joined.encode()).decode()

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
                    if link_text.endswith(".txt") or link_text.endswith(".yml") or link_text.endswith(".yaml"):
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
            urls = NodeExtractor().extract_and_encode(urls)
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
                content = NodeExtractor().extract_and_encode(content)
                
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

def print_contribution_box():
    """打印贡献节点提示框（兼容Docker环境）"""
    use_color = COLOR_SUPPORTED
    use_utf8 = UTF8_SUPPORTED

    # 根据环境选择边框字符
    if use_utf8:
        h_line = '═'
        h_div = '─'
        tl, tr, bl, br = '╔', '╗', '╚', '╝'
        dl, dr = '╠', '╣'
    else:
        h_line = '='
        h_div = '-'
        tl, tr, bl, br = '+', '+', '+', '+'
        dl, dr = '+', '+'

    inner_width = 64

    # 颜色辅助函数
    def c(text, color):
        return f"{color}{text}{RESET}" if use_color else text

    # 顶部装饰线
    top_line = h_line * (inner_width + 4)
    print(f"\n{c(top_line, YELLOW)}")

    # 顶部边框
    print(f"{c(tl + h_line * inner_width + tr, YELLOW)}")

    # 标题行
    title = "开源贡献邀请"
    icon = "*"
    title_display = get_display_width(title)
    title_padding = (inner_width - title_display - 6) // 2
    if use_utf8:
        print(f"{c('║', YELLOW)}{' ' * title_padding}{c('🌟', GREEN)} {c('【' + title + '】', CYAN)}{c('🌟', GREEN)}{' ' * title_padding}{c('║', YELLOW)}")
    else:
        print(f"{c('|', YELLOW)}{' ' * title_padding}{c('*', GREEN)} {c('[' + title + ']', CYAN)}{c('*', GREEN)}{' ' * title_padding}{c('|', YELLOW)}")

    # 分割线
    print(f"{c(dl + h_div * inner_width + dr, YELLOW)}")

    # 内容行
    if use_utf8:
        content_lines = [
            ("💡", "检测到您本地的测试节点可能有所更新", BLUE),
            ("🤝", "欢迎为开源项目贡献您的节点资源！", MAGENTA),
            ("", "", WHITE),
            ("📦", "项目地址: github.com/xuc7950/FreeNodeAggregator", CYAN),
            ("📧", "联系邮箱: xuc7950@foxmail.com", GREEN),
            ("", "", WHITE),
            ("🎓", "贡献教程: B站搜索「如何在github上贡献代码」", YELLOW),
        ]
    else:
        content_lines = [
            ("*", "检测到您本地的测试节点可能有所更新", BLUE),
            ("*", "欢迎为开源项目贡献您的节点资源！", MAGENTA),
            ("", "", WHITE),
            ("*", "项目地址: github.com/xuc7950/FreeNodeAggregator", CYAN),
            ("*", "联系邮箱: xuc7950@foxmail.com", GREEN),
            ("", "", WHITE),
            ("*", "贡献教程: B站搜索「如何在github上贡献代码」", YELLOW),
        ]

    border = '║' if use_utf8 else '|'
    for icon, text, color in content_lines:
        if icon == "":
            print(f"{c(border, YELLOW)}{' ' * inner_width}{c(border, YELLOW)}")
        else:
            line_text = f"{icon} {text}"
            line_display = get_display_width(line_text)
            padding = inner_width - line_display - 2
            print(f"{c(border, YELLOW)} {c(line_text, color)}{' ' * padding}{c(border, YELLOW)}")

    # 底部分割线
    print(f"{c(dl + h_div * inner_width + dr, YELLOW)}")

    # 感谢语
    thanks = "感谢您的支持，让开源社区更美好！"
    thanks_display = get_display_width(thanks)
    thanks_padding = (inner_width - thanks_display - 4) // 2
    if use_utf8:
        print(f"{c('║', YELLOW)}{' ' * thanks_padding}{c('❤️ ' + thanks, GREEN)}{' ' * thanks_padding}{c('║', YELLOW)}")
    else:
        print(f"{c('|', YELLOW)}{' ' * thanks_padding}{c('<3 ' + thanks, GREEN)}{' ' * thanks_padding}{c('|', YELLOW)}")

    # 底部边框
    print(f"{c(bl + h_line * inner_width + br, YELLOW)}")

    # 底部装饰线
    print(f"{c(top_line, YELLOW)}\n")