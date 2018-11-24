#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import requests
from parse import *
from config import *
import commands
import logging

def main():
    if not os.path.exists(input_file):
        commands.getstatusoutput("touch %s"%(input_file))
    url_list = []
    with open(input_file,"r") as f:
        tmp = f.read()
        map(lambda i:url_list.append(i),tmp.split("\n"))
    for i in url_list:
        valid_url = urlparse.urlparse(i)
        try:
            site = re.search("(?<=\.)\w+(?=\.)", valid_url.netloc).group()
        except Exception,e:
            logging.warning("url.txt file format maybe wrong.")
            continue
        p = Parse([i])
        p.parse()
    pass

if __name__ == '__main__':
    main()


