import requests

urls = [
    "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt",
    "https://big.oisd.nl"
]

# 黑名单和白名单配置
blacklist = [
    "||dns-tunnel-check.googlezip.net^"  # 添加你想要屏蔽的域名，使用与过滤规则相同的格式
]
whitelist = []  # 白名单暂时为空

unique_lines = set()

def download_filters(urls):
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            # 只处理非注释行
            filtered_lines = {
                line.strip() for line in response.text.splitlines()
                if not line.startswith('!') and line.strip()
            }
            unique_lines.update(filtered_lines)
        except requests.RequestException as e:
            print(f"下载失败 {url}: {e}")

def apply_blacklist_whitelist():
    # 添加黑名单规则
    unique_lines.update(blacklist)
    
    # 移除白名单中的规则
    if whitelist:
        unique_lines.difference_update(whitelist)

def save_to_file(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(unique_lines)) + '\n')

def main():
    # 下载过滤规则
    download_filters(urls)
    
    # 应用黑白名单
    apply_blacklist_whitelist()
    
    # 保存到文件
    save_to_file("dns_filters.txt")
    print(f"过滤规则文件 'dns_filters.txt' 已创建，共 {len(unique_lines)} 条规则")
    print(f"其中包含 {len(blacklist)} 条黑名单规则")
    print(f"白名单规则数量: {len(whitelist)}")

if __name__ == "__main__":
    main()
