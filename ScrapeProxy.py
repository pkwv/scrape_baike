# -*- coding:utf8 -*-

import MySQLdb
from lxml import etree
import MyRequest
import ConnMysql
import time
import random
import threading

class ScrapeProxy(threading.Thread):
    def __init__(self, thread_name, max_num, gap):
        super(ScrapeProxy, self).__init__()
        self.thread_name = thread_name
        self.max_num = max_num
        self.gap = gap
    def is_ip(self, ip):
        num = 0
        for i in ip:
            if i == '.':
                num += 1
        return num == 3
    def is_port(self, ip):
        for i in ip:
            if ord(i) <= ord('0') or ord(i) >= ord('9') :
                return False
        return True
    def run(self):
        while True:
            conn = ConnMysql.ConnMysql()
            cur = conn.cursor()
            cur.execute("select * from proxies")
            n = cur.rowcount
            if n > self.max_num:
                time.sleep(self.gap*0.8*random.uniform(0.75,1.25))
                continue
            url = 'http://www.xicidaili.com/nn'
            res = MyRequest.MyRequest(url, False)
            t = etree.HTML(res.text)
            l = t.xpath('//tr[@class="" or @class="odd"]/td/text()')
            for i in l:
                if self.is_ip(i):
                    ip = i
                if self.is_port(i):
                    proxy = 'http://' + ip + ':' + i
                    conn = ConnMysql.ConnMysql()
                    cur = conn.cursor()
                    cur.execute("insert into proxies set url=%s on duplicate key update url=%s",(proxy,proxy,))
                    conn.commit()
                    cur.close()
                    conn.close()
            time.sleep(self.gap*random.uniform(0.75,1.25))
