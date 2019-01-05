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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions
from selenium.webdriver.common.proxy import *
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

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


dcap = dict(DesiredCapabilities.PHANTOMJS)
#pc端的ua
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.94 Ch"
    "rome/62.0.3202.94 Safari/537.36"
        )


class Parse(object):
    def __init__(self,url):
        self.site = self.get_site(url)
        self.url = url
        self.headers = {"User-Agent":random.choice(User_Agent)}
        #建立无头浏览器，for渲染页面
        self.driver = webdriver.PhantomJS()
    def get_site(self,url):
        #使用第一个传入元素标识，在传进来下载之前，自动分好类
        try:
            valid_url = urlparse.urlparse(url[0])
            #print valid_url.netloc
            #暂时只有纵横没有前缀，其他的前缀是：www 或者 book
            if re.search("www",valid_url.netloc) or re.search("book",valid_url.netloc):
                site = re.search("(?<=\.)\w+(?=\.)",valid_url.netloc).group()
            else:
                site = re.search("^\w+(?=\.)",valid_url.netloc).group()
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

    def fetch(self,url,headers={}):
        if not type(headers) == dict:
            #不符合条件不添加
            return requests.get(url,headers=self.headers).content
        for k,v in headers.items():
            if self.headers.get(k):
                continue
            self.headers[k] = v
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
        if isinstance(self.url,list):
            for url in self.url:
                try:
                    res = PyQuery(self.fetch(url))
                    bookname = res('.title > a > b').text().strip().replace(" ", "")
                    # 下载页面
                    name = bookname.encode("utf-8") + ".txt"
                    print name
                    detail_url = []
                    self.exists(name)
                    #详细章节分页面
                    #print detail_url
                    detail_url = res('.btnlist a:nth-of-type(2)').attr.href
                    print detail_url
                    detail_res = PyQuery(self.fetch(detail_url))
                    count = 0
                    #此时char为 卷数，弟几卷
                    for char, tmp in enumerate(detail_res('.list').items()):
                        if re.search("VIP卷",tmp('.f900').text().strip().encode('utf-8')):
                            #logging.info("VIP卷，直接跳过，第 %d 卷"%(char))
                            continue
                        #if char < 16:
                        #    continue
                        for i in tmp(".block_ul li a").items():
                            url = i.attr.href
                            #print url
                            if not url:
                                # logging.warning("章节[%s]被锁住，没法不能查看."%(title))
                                continue
                            """
                            #通常的访问无法获取到内容
                            #print i
                            #res = PyQuery(self.fetch(url))
                            #res = PyQuery(self.fetch(url,headers={"Cookie":"pgv_pvid=8964445305; pac_uid=0_d6480855a5bb2; pgv_pvi=969894912; tvfe_boss_uuid=c0772c324f2a1036; bdshare_firstime=1537089727537; readBeginnerGuide=1; pgv_si=s1909591040; qqmusic_fromtag=66; PHPSESSID=k4r31aa42vm39k3ru88n5rekv6; pgv_info=ssid=s9063563124&pgvReferrer=; d_rh_new=1001760719.66-22532547.366; mr3=czo2NDoiAFsGWwUxBjIMMAk4UzcDYwAwVDFYbAFmUnwHM1QyVAUPIwlUVGMDNVhhXW5bOlEyCDxSN1Z%2FDWBSZgIxVl0MXSI7; ied_rf=chuangshi.qq.com/bk/ds/AGkENF1gVjYAPVRiATEBYw1vBzw-r-67.html"}))
                            
                            print res.text() 
                            title = res('.chapterTitle').text().strip().encode('utf-8')
                            text = res('.bookreadercontent').text().encode('utf-8')
                            """
                            #重试3次
                            retry_time = 0
                            flag = 0
                            while((retry_time < 3) and (not flag)):
                                try:
                                    driver = webdriver.PhantomJS()
                                    driver.set_page_load_timeout(3)
                                    driver.get(url)
                                    title = driver.find_element_by_xpath("//*[@data-node='chapterTitle']").text.encode('utf-8')
                                    text = driver.find_element_by_xpath("//*[@class='bookreadercontent']").text.encode('utf-8')
                                    #print text
                                    #这边count才是章节数，char是卷数
                                    self.save(name, "[tingyun--%s]" % (count) + title + "\n\n" + text + "\n\n")
                                    #关闭所有窗口，直接退出浏览器
                                    driver.quit()
                                    count += 1
                                    flag = 1
                                except Exception,e:
                                    logging.warning(e)
                                    retry_time += 1
                            
                            # 下载时延
                            time.sleep(DOWNLOAD_DELAY)
                except Exception, e:
                    logging.warning("download error [%s] , [%s]" % (url, e))
        pass

    def xxsy(self):
        if isinstance(self.url,list):
            for url in self.url:
                try:
                    res = PyQuery(self.fetch(url))
                    bookname = res('h1').text().strip().replace(" ", "")
                    # 下载页面
                    name = bookname.encode("utf-8") + ".txt"
                    print name
                    detail_url = []
                    self.exists(name)
                    #print res('.catalog-list').text()
                    #"http://www.xxsy.net/partview/GetChapterList?bookid=1073941&noNeedBuy=1&special=0&maxFreeChapterId=0"
                    bookid = re.search("\d+(?=\.html)",url).group()
                    #print bookid
                    detail_url =  "http://www.xxsy.net/partview/GetChapterList?bookid=%s&noNeedBuy=1&special=0&maxFreeChapterId=0"%(bookid)
                    #详细章节分页面
                    #print detail_url
                    
                    detail_res = PyQuery(self.fetch(detail_url))
                    for char, tmp in enumerate(detail_res('[class="catalog-list cl"] li a').items()):
                        #if char < 16:
                        #    continue
                        url = tmp.attr.href
                        #print url
                        if not url:
                            # logging.warning("章节[%s]被锁住，没法不能查看."%(title))
                            continue
                        url = "http://" + urlparse.urlparse(detail_url).netloc + url
                        print url
                        res = PyQuery(self.fetch(url))
                        title = res('.chapter-title').text().strip().encode('utf-8')
                        text = res('.chapter-main').text().encode('utf-8')
                        self.save(name, "[tingyun--%s]" % (char) + title + "\n\n" + text + "\n\n")
                        # 下载时延
                        time.sleep(DOWNLOAD_DELAY)
                        
                except Exception, e:
                    logging.warning("download error [%s] , [%s]" % (url, e))
        
        pass
    def zongheng(self):
        if isinstance(self.url,list):
            for url in self.url:
                try:
                    res = PyQuery(self.fetch(url))
                    bookname = res('.book-name').text().strip().replace(" ", "")
                    # 下载页面
                    name = bookname.encode("utf-8") + ".txt"
                    print name
                    detail_url = []
                    self.exists(name)
                    detail_url = res('.all-catalog').attr.href
                    #详细章节分页面
                    #print detail_url
                    detail_res = PyQuery(self.fetch(detail_url))
                    #vip的类型是class="vip col-4"
                    for char, tmp in enumerate(detail_res('[class=" col-4"] > a').items()):
                        #if char < 16:
                        #    continue
                        url = tmp.attr.href
                        #print url
                        if not url:
                            # logging.warning("章节[%s]被锁住，没法不能查看."%(title))
                            continue
                        res = PyQuery(self.fetch(url))
                        title = res('.title_txtbox').text().strip().encode('utf-8')
                        text = res('.content').text().encode('utf-8')
                        self.save(name, "[tingyun--%s]" % (char) + title + "\n\n" + text + "\n\n")
                        # 下载时延
                        time.sleep(DOWNLOAD_DELAY)
                        
                except Exception, e:
                    logging.warning("download error [%s] , [%s]" % (url, e))
        
        pass

    def jjwxc(self):
        if isinstance(self.url,list):
            for url in self.url:
                try:
                    res = PyQuery(self.fetch(url))
                    bookname = res('[itemprop="articleSection"]').text().strip().replace(" ", "")
                    # 下载页面
                    name = bookname.encode("utf-8") + ".txt"
                    print name
                    detail_url = []
                    self.exists(name)
                    for char, tmp in enumerate(res('[itemprop="url"]').items()):
                        #if char < 16:
                        #    continue
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
                    logging.warning("download error [%s] , [%s]" % (url, e))
        pass

if __name__ == '__main__':
    #test
    #test = Parse([]).parse()
    #test = Parse(["https://book.qidian.com/info/1004608738"]).parse()
    #test = Parse(["http://www.jjwxc.net/onebook.php?novelid=472870"]).parse()
    #test = Parse(["http://book.zongheng.com/book/578305.html"]).parse()
    #test = Parse(["http://www.xxsy.net/info/1073941.html"]).parse()
    #test = Parse(["http://chuangshi.qq.com/bk/ds/1001760719.html"]).parse()

    pass
