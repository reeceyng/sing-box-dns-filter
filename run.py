import requests
import sys
from typing import List, Set

# --- 配置 ---
FILTER_URLS: List[str] = [
    "https://big.oisd.nl"
]
OUTPUT_FILENAME: str = "temp_filters.txt"
REQUEST_TIMEOUT: int = 15 # 增加超时时间

# --- 全局变量 ---
unique_lines: Set[str] = set()

def download_filters(urls: List[str], session: requests.Session) -> bool:
    """
    从给定的 URL 列表下载过滤规则。

    Args:
        urls: 包含过滤规则 URL 的列表。
        session: requests.Session 对象用于网络请求。

    Returns:
        True 如果至少成功下载并处理了一个 URL, False 否则。
    """
    success_count = 0
    for url in urls:
        print(f"Processing URL: {url}")
        try:
            # 使用 Session 发送请求
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status() # 如果状态码不是 2xx，则抛出 HTTPError

            print(f"  Status Code: {response.status_code}")
            raw_lines = response.text.splitlines()
            print(f"  Original line count: {len(raw_lines)}")

            # 处理每一行：去除首尾空格，忽略空行和注释行('!'开头)
            filtered_lines = {
                line.strip() for line in raw_lines
                if line.strip() and not line.startswith('!')
            }

            print(f"  Filtered line count: {len(filtered_lines)}")
            unique_lines.update(filtered_lines)
            success_count += 1

        except requests.Timeout:
            print(f"  Error: Timeout occurred while downloading {url}")
        except requests.HTTPError as e:
            print(f"  Error: HTTP error occurred for {url}: {e}")
        except requests.RequestException as e:
            print(f"  Error: Failed to download {url}: {e}")
        except Exception as e:
            print(f"  Error: An unexpected error occurred processing {url}: {e}")

    return success_count > 0

def save_to_file(filename: str, lines: Set[str]):
    """
    将处理后的规则行写入文件，按字母顺序排序。

    Args:
        filename: 输出文件名。
        lines: 包含要去重的规则行的集合。
    """
    if not lines:
        print("Warning: No lines collected. Output file will be empty or not created.")
        # 根据需要决定是创建空文件还是不创建
        # 这里选择创建空文件，以便 sing-box 不会因找不到文件而报错，但结果srs也可能是空的
        # 或者你可以选择在这里退出 sys.exit(1)

    print(f"Sorting {len(lines)} unique lines...")
    sorted_lines = sorted(list(lines)) # 转换为列表进行排序

    print(f"Saving unique lines to '{filename}'...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # 每行写入，并在文件末尾添加一个换行符
            f.write('\n'.join(sorted_lines))
            f.write('\n') # 确保文件末尾有换行符
        print(f"Successfully saved {len(sorted_lines)} lines to '{filename}'.")
    except IOError as e:
        print(f"Error: Failed to write to file {filename}: {e}")
        sys.exit(1) # 写入文件失败是严重错误，退出

def main():
    """
    主函数：下载、处理并保存过滤规则。
    """
    print("Starting filter download process...")
    # 创建 Session 对象
    with requests.Session() as session:
        # 设置通用的请求头，模拟浏览器
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })
        if not download_filters(FILTER_URLS, session):
            print("Error: All filter downloads failed. Exiting.")
            sys.exit(1) # 所有下载都失败，则退出

    # 只有在下载成功后才保存文件
    save_to_file(OUTPUT_FILENAME, unique_lines)
    print(f"Process finished. {len(unique_lines)} unique lines collected.")

if __name__ == "__main__":
    main()
