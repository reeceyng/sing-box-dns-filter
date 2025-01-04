import requests

urls = [
    "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt",
    "https://big.oisd.nl"
]

unique_lines = set()
blacklist = set([
    "||dns-tunnel-check.googlezip.net^",
])

whitelist = set()

def download_filters(urls):
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            for line in response.text.splitlines():
                stripped_line = line.strip()
                if stripped_line.startswith('!'):
                    continue
                if stripped_line in blacklist:
                    unique_lines.add(stripped_line)
                elif stripped_line not in whitelist:
                    unique_lines.add(stripped_line)
        except requests.RequestException as e:
            print(f"Download failed for {url}: {e}")

def save_to_file(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(unique_lines) + '\n')

def main():
    download_filters(urls)
    save_to_file("temp_filters.txt")
    print(f"Temporary file 'temp_filters.txt' created with {len(unique_lines)} lines.")

if __name__ == "__main__":
    main()
