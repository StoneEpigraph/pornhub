#!/usr/bin/env python
# coding=utf-8

import os
import urllib
import json
import re

import multiprocessing
import requests
from lxml import etree
import fire
from loguru import logger
logger.add("logs/%s.log" % 'log', format="{time:MM-DD HH:mm:ss} {level} {message}")

User_Agents = ["Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_2 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_2 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5",
    "MQQBrowser/25 (Linux; U; 2.3.3; zh-cn; HTC Desire S Build/GRI40;480*800)",
    "Mozilla/5.0 (Linux; U; Android 2.3.3; zh-cn; HTC_DesireS_S510e Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (SymbianOS/9.3; U; Series60/3.2 NokiaE75-1 /110.48.125 Profile/MIDP-2.1 Configuration/CLDC-1.1 ) AppleWebKit/413 (KHTML, like Gecko) Safari/413",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Mobile/8J2",
    "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A5313e Safari/7534.48.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A5313e Safari/7534.48.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A5313e Safari/7534.48.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; SAMSUNG; OMNIA7)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; XBLWP7; ZuneWP7)",
    "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30",
    "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)",
    "Mozilla/4.0 (compatible; MSIE 60; Windows NT 5.1; SV1; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; TheWorld)"]



headers = {
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
}


def list_page(url):
    logger.info('crawling : %s' % url)
    proxies = {'http': 'http://localhost:1080', 'https': 'http://localhost:1080'}
    resp = requests.get(url, proxies=proxies, headers=headers)
    # resp = requests.get(url, headers=headers)
    html = etree.HTML(resp.text)
    vkeys = html.xpath('//*[@class="phimage"]/div/a/@href')
    gif_keys = html.xpath('//*[@class="phimage"]/div/a/img/@data-mediabook')
    # jobs = []
    for i in range(len(vkeys)):
        item = {}
        item['vkey'] = vkeys[i].split('=')[-1]
        item['gif_url'] = gif_keys[i]
        try:
            if 'ph' in item['vkey']:
                # jobs.append(gevent.spawn(download, item['gif_url'], item['vkey'],'webm'))
                p = multiprocessing.Process(target=download, args=(item['gif_url'], item['vkey'], 'webm'))
                p.start()
        except Exception as err:
            logger.error(err)
    # gevent.joinall(jobs, timeout=2)


def detail_page(url):
    proxies = {'http': 'http://localhost:1080', 'https': 'http://localhost:1080'}
    s = requests.Session()
    resp = s.get(url, proxies=proxies, headers=headers)
    html = etree.HTML(resp.content)
    title = ''.join(html.xpath('//h1//text()')).strip()

    js = html.xpath('//*[@id="player"]/script/text()')[0]
    tem = re.findall('var\\s+\\w+\\s+=\\s+(.*);\\s+var player_mp4_seek',js)[-1]
    con = json.loads(tem)

    for _dict in con['mediaDefinitions']:
        if 'quality' in _dict.keys() and _dict.get('videoUrl'):
            logger.info('%s %s' % (_dict.get('quality'), _dict.get('videoUrl')))
            try:
                download(_dict.get('videoUrl'), title, 'mp4')
                break  # 如下载了较高分辨率的视频 就跳出循环
            except Exception as err:
                logger.error(err)


def download(url, name, filetype):
    filepath = '%s/%s.%s' % (filetype, name, filetype)
    if os.path.exists(filepath):
        logger.info('this file had been downloaded :: %s' % filepath)
        return
    proxy = urllib.request.ProxyHandler({'http': 'http://localhost:1080', 'https': 'http://localhost:1080'})
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)
    logger.info('url: ' + url)
    urllib.request.urlretrieve(url, '%s' % filepath)
    logger.info('download success :: %s' % filepath)

def download_test():
    url = 'http://www.google.com'
    name = 'google'
    filetype = 'mp4'
    download(url, name, filetype)


def run(_arg=None):
    paths = ['webm', 'mp4', 'list']
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)
    if _arg == 'webm':
        # https://www.pornhub.com/categories
        urls = [
            'https://www.pornhub.com/video?o=tr',
            'https://www.pornhub.com/video?o=ht',
            'https://www.pornhub.com/video?o=mv',
            'https://www.pornhub.com/video'
        ]
        # jobs = [gevent.spawn(list_page, url) for url in urls]
        # gevent.joinall(jobs)
        for url in urls:
            p = multiprocessing.Process(target=list_page, args=(url, ))
            p.start()
    elif _arg == 'mp4':
        with open('download.txt', 'r') as file:
            keys = list(set(file.readlines()))
        # jobs = []
        for key in keys:
            if not key.strip():
                continue
            url = 'https://www.pornhub.com/view_video.php?viewkey=%s' % key.strip()
            logger.info('url: {}', url)
            # jobs.append(gevent.spawn(detail_page, url))
            p = multiprocessing.Process(target=detail_page, args=(url, ))
            p.start()
        # gevent.joinall(jobs, timeout=2)
    elif _arg == 'list':
        root_dir = os.path.dirname(os.path.abspath(__file__))
        curr_dir = root_dir + os.path.sep + 'webm' + os.path.sep
        file_list = os.listdir(curr_dir)
        download_seeds = ''
        for i in range(0, len(file_list)):
            path = file_list[i].split('.')[0]
            download_seeds += path + '\n'
        seed_file_name = root_dir + os.path.sep + 'download.txt'
        f = open(seed_file_name, 'w+')
        f.write(download_seeds)
        f.close()
        return
    else:
        _str = """
tips:
    python crawler.py webm
        - 下载热门页面的缩略图，路径为webm文件夹下

    python crawler.py mp4
        - 将下载的webm文件对应的以ph开头的文件名逐行写在download.txt中，运行该命令
        """
        logger.info(_str)
    logger.info('Using multiprocessing, commands send to system, please wait a moment.')
    logger.info('Maybe there is some error, leave it alone.')


if __name__ == '__main__':
    fire.Fire(run)


