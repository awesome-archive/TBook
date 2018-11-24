#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

from config import *
import urlparse
import logging
import re
import requests
import random
from pyquery import PyQuery
import os
import commands
import time


file_name = __file__.split('/')[-1].replace(".py","")
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='%s.log'%file_name,
                filemode='a')

#将日志打印到标准输出（设定在某个级别之上的错误）
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-6s %(lineno)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class Parse(object):
    def __init__(self,url):
        self.site = self.get_site(url)
        self.url = url
        self.headers = {"User-Agent":random.choice(User_Agent)}

    def get_site(self,url):
        #使用第一个传入元素标识，在传进来下载之前，自动分好类
        try:
            valid_url = urlparse.urlparse(url[0])
            #print type(valid_url.netloc)
            site = re.search("(?<=\.)\w+(?=\.)",valid_url.netloc).group()
        except Exception,e:
            logging.warning("get site [%s] error."%(url))
            return WRONG_SITE
        return site

    def parse(self):
        site_type = site_map.get(self.site)
        if site_type != None:
            logging.info("begin parse site : [%s]"%(self.site))
            if site_type == 1:
                self.qidian()
            elif site_type == 2:
                self.chuangshi()
            elif site_type == 3:
                self.xxsy()
            elif site_type == 4:
                self.zongheng()
            elif site_type == 5:
                self.jjwxc()
            else:
                pass

        else:
            logging.warning("site [%s] is not valid "%(self.site))
    def exists(self,name):
        local_dir = "%s/%s" % (output_file_pre,self.site)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        local_file = local_dir + "/" + name
        print local_file
        if os.path.exists(local_file):
            logging.warning("file exists , delete , redownload.")
            if commands.getstatusoutput("rm -f %s" % (local_file))[0] != 0:
                logging.warning("delete filed ，please check file [%s] exists." % (local_file))

    def save(self,name,content):
        local_dir = "%s/%s"%(output_file_pre,self.site)
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        local_file = local_dir + "/" + name
        with open(local_file,'a') as f:
            f.write(content)
            f.close()
        pass

    def fetch(self,url):
        return requests.get(url,headers=self.headers).content

    def qidian(self):
        #list url
        if isinstance(self.url,list):
            for url in self.url:
                try:
                    bookname = PyQuery(requests.get(url).content)('h1 > em').text().strip().replace(" ", "")
                    name = bookname.encode("utf-8") + ".epub"
                    self.exists(name)
                    bookid = re.search("\d+", url).group()
                    download_url = "http://download.qidian.com/epub/%s.epub" % (bookid)
                    content = requests.get(download_url).content
                    self.save(name, content)
                except Exception, e:
                    logging.warning("download error [%s]" % (url))
        pass

    def chuangshi(self):
        pass

    def xxsy(self):
        pass

    def zongheng(self):
        pass

    def jjwxc(self):
        if isinstance(self.url,list):
            for url in self.url:
                try:
                    res = PyQuery(self.fetch(self.url))
                    bookname = res('[itemprop="articleSection"]').text().strip().replace(" ", "")
                    # 下载页面
                    name = bookname.encode("utf-8") + ".txt"
                    print name
                    detail_url = []
                    self.exists(name)
                    for char, tmp in enumerate(res('[itemprop="url"]').items()):
                        if char < 16:
                            continue
                        url = tmp.attr.href
                        if not url:
                            # logging.warning("章节[%s]被锁住，没法不能查看."%(title))
                            continue
                        res = PyQuery(self.fetch(url))
                        title = res('h2').text().strip().encode('utf-8')
                        # 剔除掉div，只取文本
                        text = res('.noveltext').remove('div').text().encode('utf-8')
                        self.save(name, "[tingyun--%s]" % (char) + title + "\n\n" + text + "\n\n")
                        # 下载时延
                        time.sleep(DOWNLOAD_DELAY)

                except Exception, e:
                    logging.warning("download error [%s] , [%s]" % (self.url, e))
        pass

if __name__ == '__main__':
    #test
    #test = Parse([]).parse()
    test = Parse(["https://book.qidian.com/info/1004608738"]).parse()
    #test = Parse(["http://www.jjwxc.net/onebook.php?novelid=472870"]).parse()

    pass
