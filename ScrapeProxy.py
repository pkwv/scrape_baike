# -*- coding:utf8 -*-

import MySQLdb
from lxml import etree
import MyRequest
import ConnMysql
import time
import random
import threading
import requests

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
        if ip == '':
            return False
        for i in ip:
            if ord(i) < ord('0') or ord(i) > ord('9') :
                return False
        return True
    def insert_mysql(self, ip):
        conn = ConnMysql.ConnMysql()
        cur = conn.cursor()
        for proxy in ip:
            cur.execute("insert into proxies set url=%s on duplicate key update url=%s",(proxy,proxy,))
        conn.commit()
        cur.close()
        conn.close()

    def process_ip_port(self, lst):
        proxy = []
        for i in lst:
            i = i.strip()
            if self.is_ip(i):
                ip = i
            if self.is_port(i):
                proxy.append('http://' + ip + ':' + i)
        return proxy

    def scrape_89ip(self):
        payload = {'tqsl':'30'}
        url = 'http://www.89ip.cn/tiqu.php'
        res = requests.get(url, params = payload)
        t = etree.HTML(res.text)
        lst = t.xpath('//div[@class="mass"]/text()')
        ip = []
        for i in lst:
            i = i.strip()
            dot = 0
            colon = 0
            for j in i:
                if j == '.':
                    dot += 1
                if j == ':':
                    colon += 1
            if dot == 3 and colon == 1:
                ip.append('http://' + i)
        self.insert_mysql(ip)
    
    def scrape_extract(self, url, p):
        res = MyRequest.MyRequest(url, False)
        t = etree.HTML(res.text)
        l = t.xpath(p)
        proxy = self.process_ip_port(l)
        self.insert_mysql(proxy)
        
    def scrape_xici(self):
        url = 'http://www.xicidaili.com/nn'
        p = '//tr[@class="" or @class="odd"]/td/text()'
        self.scrape_extract(url, p)

    def scrape_http(self):
        url = 'http://www.httpdaili.com/mfdl/'
        p = '//li[@style="position: absolute; left: 10.5px; top: 0px;"]//div[@class="kb-item-wrap11"]//td/text()'
        self.scrape_extract(url, p)
        
    def scrape_fldd(self):
        url = 'http://www.fldd.cn/index.asp'
        p = '//tr[@class="odd"]/td[@class="style1" or @class="style2"]/text()'
        self.scrape_extract(url, p)
    
    def scrape_hao(self):
        url = 'http://www.haodailiip.com/guonei'
        p = '//table[@class="proxy_table"]//tr/td/text()'
        self.scrape_extract(url, p)
    
    def scrape_kuai(self):
        url = 'http://www.kuaidaili.com/free/inha/1/'
        p = '//table[@class="table table-bordered table-striped"]//tr/td/text()'
        self.scrape_extract(url, p)
        
    def run(self):
        while True:
            conn = ConnMysql.ConnMysql()
            cur = conn.cursor()
            cur.execute("select * from proxies")
            n = cur.rowcount
            print n
            print self.max_num
            if n > self.max_num:
                time.sleep(self.gap*0.8*random.uniform(0.75,1.25))
                continue
            print 'scrape'
            self.scrape_89ip()     #
            self.scrape_xici()     # ok
            self.scrape_http()     # ok
            self.scrape_fldd()     # ok
            self.scrape_hao()      # ok
            self.scrape_kuai()     # ok
            time.sleep(self.gap*random.uniform(0.75,1.25))
