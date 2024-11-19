#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import json
from datetime import datetime, timezone, timedelta
from pythonping import ping
from requests_html import HTMLSession
from retry import retry

# GitHub 域名列表
GITHUB_URLS = [
    'alive.github.com', 'api.github.com', 'assets-cdn.github.com',
    'avatars.githubusercontent.com', 'avatars0.githubusercontent.com',
    'avatars1.githubusercontent.com', 'avatars2.githubusercontent.com',
    'avatars3.githubusercontent.com', 'avatars4.githubusercontent.com',
    'avatars5.githubusercontent.com', 'camo.githubusercontent.com',
    'central.github.com', 'cloud.githubusercontent.com', 'codeload.github.com',
    'collector.github.com', 'desktop.githubusercontent.com',
    'favicons.githubusercontent.com', 'gist.github.com',
    'github-cloud.s3.amazonaws.com', 'github-com.s3.amazonaws.com',
    'github-production-release-asset-2e65be.s3.amazonaws.com',
    'github-production-repository-file-5c1aeb.s3.amazonaws.com',
    'github-production-user-asset-6210df.s3.amazonaws.com', 'github.blog',
    'github.com', 'github.community', 'github.githubassets.com',
    'github.global.ssl.fastly.net', 'github.io', 'github.map.fastly.net',
    'githubstatus.com', 'live.github.com', 'media.githubusercontent.com',
    'objects.githubusercontent.com', 'pipelines.actions.githubusercontent.com',
    'raw.githubusercontent.com', 'user-images.githubusercontent.com',
    'vscode.dev', 'education.github.com', 'private-user-images.githubusercontent.com'
]

HOSTS_TEMPLATE = """# GitHub520 Host Start
{content}

# Update time: {update_time}
# GitHub520 Host End\n"""


def write_host_file(hosts_content: str) -> None:
    """将 hosts 内容写入文件"""
    output_file_path = "/www/wwwroot/tv.jason888.eu.org/githubhosts/hosts"
    with open(output_file_path, "w") as output_fb:
        output_fb.write(hosts_content)


def write_json_file(hosts_list: list) -> None:
    """将域名-IP 对应关系写入 JSON 文件"""
    output_file_path = "/www/wwwroot/tv.jason888.eu.org/githubhosts/hosts.json"
    with open(output_file_path, "w") as output_fb:
        json.dump(hosts_list, output_fb)


def get_best_ip(ip_list: list) -> str:
    """从 IP 列表中选择延迟最低的 IP"""
    ping_timeout = 2
    best_ip = ''
    min_ms = ping_timeout * 1000
    ip_set = set(ip_list)
    for ip in ip_set:
        ping_result = ping(ip, timeout=ping_timeout)
        print(f"Ping {ip}: {ping_result.rtt_avg_ms}ms")
        if ping_result.rtt_avg_ms == ping_timeout * 1000:
            continue  # 超时认为 IP 失效
        if ping_result.rtt_avg_ms < min_ms:
            min_ms = ping_result.rtt_avg_ms
            best_ip = ip
    return best_ip


@retry(tries=3)
def get_ip(session: HTMLSession, github_url: str) -> str:
    """通过网站解析获取指定域名的 IP 地址"""
    url = f'https://sites.ipaddress.com/{github_url}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    try:
        rs = session.get(url, headers=headers, timeout=10)
        pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        ip_list = re.findall(pattern, rs.html.text)
        best_ip = get_best_ip(ip_list)
        if best_ip:
            return best_ip
        raise Exception(f"No valid IP found for {github_url}")
    except Exception as ex:
        print(f"Failed to get IP for {github_url}: {ex}")
        raise


def main(verbose=False) -> None:
    """主逻辑"""
    if verbose:
        print("Start script.")

    session = HTMLSession()
    content = ""
    content_list = []

    for index, github_url in enumerate(GITHUB_URLS):
        try:
            ip = get_ip(session, github_url)
            content += ip.ljust(30) + github_url + "\n"
            content_list.append((ip, github_url))
        except Exception as ex:
            print(f"Error processing {github_url}: {ex}")
        if verbose:
            print(f"Processed {index + 1}/{len(GITHUB_URLS)}")

    if not content:
        print("No content generated. Exiting.")
        return

    update_time = datetime.now(timezone.utc).astimezone(
        timezone(timedelta(hours=8))
    ).replace(microsecond=0).isoformat()

    hosts_content = HOSTS_TEMPLATE.format(content=content, update_time=update_time)

    # 写入文件
    write_host_file(hosts_content)
    write_json_file(content_list)

    if verbose:
        print(hosts_content)
        print("End script.")


if __name__ == '__main__':
    main(True)
