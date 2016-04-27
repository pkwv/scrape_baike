# -*- coding:utf-8 -*- 

import re
import json
from datetime import datetime
from hashlib import md5
import threading
import thread
import urllib
import urllib2
from lxml import etree
import MySQLdb
import MySQLdb.cursors
import time
import user_agent
import setting
import random
import codecs

MYSQL_HOST = setting.MYSQL_HOST 
MYSQL_DBNAME = setting.MYSQL_DBNAME
MYSQL_USER = setting.MYSQL_USER
MYSQL_PASSWD = setting.MYSQL_PASSWD
finish = 0
item_cnt = 0
URL_START = 100
URL_END = 200
THREAD_NUM = 1
f = codecs.open('tmp.txt','w','utf-8')

class MultiScraper(threading.Thread):
    def __init__(self, thread_id, st, ed):
        super(MultiScraper, self).__init__()
        self.thread_id = thread_id
        self.st = st
        self.ed = ed
        self.cnt = 0
        self.error = 0
        self.url = ""
    def print_msg(self, content):
        print str(self.thread_id) + ' ' + content
    
    def print_cnt(self):
        print '~~~~' + str(self.thread_id) + ' ' + str(self.cnt) + ' error ' + str(self.error)
    
    def make_request(self, url):
        self.url = url
        ind = random.randint(0,len(user_agent.USER_AGENTS)-1)
        #header = {'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
        header = {'User-Agent':user_agent.USER_AGENTS[ind]}
        #print header['User-Agent']
        data = urllib.urlencode({})
        return urllib2.Request(url, data,  header)

    def add_error(self, url):
        self.error += 1
        url = self.get_url(url)
        conn = self.CONN()
        cur = conn.cursor()
        cur.execute("select 1 from error_page where url = %s",(url,))
        res = cur.fetchone()
        if not res:
            #already in error
            #maybe can not visit here!
            cur.execute("insert into error_page (url) values(%s)",(url,))
        conn.commit()
        cur.close()
        conn.close()
    def run(self):
        i = self.st
        while i < self.ed:
            ''' just do it'''
            url = 'http://baike.baidu.com/view/' + str(i) + '.htm'
            req = self.make_request(url)
            try:
                res = urllib2.urlopen(req)
            except:
                self.print_msg(url + ' run')
                i += 1
                continue
            #print url
            if 'error' in res.url:
                self.add_error(url)
            else:
                self.parse(res)
            i += 1
            t = random.uniform(0.05,0.35)
            time.sleep(t)
            if i%1000 == 0:
                self.print_msg(str(i))

    def parse(self, res):
        # url do not contain 'error' 
        if 'subview' in res.url:
            sel = etree.HTML(res.read().decode('UTF-8'))
            suburl = sel.xpath('//ul[@class="polysemantList-wrapper cmn-clearfix"]//li/a/@href')
            for url in suburl:
                url = 'http://baike.baidu.com'+url
                req = self.make_request(url)
                try:
                    r = urllib2.urlopen(req)
                except:
                    self.print_msg(url + 'subview')
                    continue
                if 'error' in r.url:
                    self.add_error(url)
                else:
                    self.parse_item(r)
        self.parse_item(res)
    def get_url(self, url):
        res = ''
        for i in url:
            if i == '#' or i == '?':
                break
            res += i
        return res

    def hashmd5(self,s):
        res=0
        for i in s:
            j = ord(i)
            if j >= ord('0') and j <= ord('9'):
                c = j - ord('0')
            else: 
                c = j - ord('a')            
            res = (res*23 + c)%10
        return res

    def link_list(self,lst):
        res=''
        for i in lst:
            res +=i
        return  res
    def CONN(self):
        return MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWD, db=MYSQL_DBNAME,charset='utf8')
    
    def parse_item(self, res):
        global item_cnt
        item_cnt += 1
        # res.url don't have 'error'
        try:
            sel = etree.HTML(res.read().decode('UTF-8'))
        except:
            #print self.thread_id+' res read error ' + res.url
            req = self.make_request(res.url)
            res = urllib2.urlopen(req)
            # there maybe can not open the url 
            # but i didn't deal with it 
            # cause it's little
            try: 
                sel = etree.HTML(res.read().decode('UTF-8'))
            except:
                self.print_msg(res.url)
                return 
        url = self.get_url(res.url)
        urlmd5id = md5(url).hexdigest()
        now = datetime.utcnow().replace(microsecond=0).isoformat(' ')

        ind = self.hashmd5(urlmd5id)
       
        title=self.link_list(sel.xpath('//head/title/text()'))
        #item['url'] = str(response.url)
        #print 'here'
        photo_e=sel.xpath('//a[@class="image-link"]//img[@class="lazy-img"]/@data-src')
        photo = ''
        for i in photo_e:
            photo += i+';'
       
        #print item['url']
        word=self.link_list(sel.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()'))  #utf8
        explanation=self.link_list(sel.xpath('string(//div[@class="lemma-summary"])'))   #utf8
        f.write(word)
        if word == '' or explanation == '':
            return
        l1=sel.xpath('//div[@class="basic-info cmn-clearfix"]//dl//dt//text()')
        l2=sel.xpath('//div[@class="basic-info cmn-clearfix"]//dl//dd//text()')
        dict={}
        j=0
        l2_len=len(l2)
        for i in l1:
            while j < l2_len:
                if l2[j] != '\n':
                    break;
                j += 1
            dict[i]=l2[j]
        #item['summarize']=json.dump(dict)   # json
        summarize=json.JSONEncoder().encode(dict)
        full_text=self.link_list(sel.xpath('//div[contains(concat(" ", @class, " "), " para-title ")]//text() |'
                                   ' //div[@class="para" and @label-module="para"]//text()'))
#        full_text=full_text.decode('utf8')
        collect=''
        like=''
        share=''
        reference=self.link_list(\
            sel.xpath('//dd[@class="reference-list-wrap"]//span[@class="text"]/text()'))
        tag=self.link_list(sel.xpath('//dd[@id="open-tag-item"]/span/text()'))
        time=self.link_list(sel.xpath('//dd[@class="description"]/ul//li/span[@class="j-modified-time"]/text()'))
        author=self.link_list(sel.xpath('//dd[@class="description"]/ul//li/a[@class="show-userCard"]/text()'))
        view=''
        if 'view' in url:
            wordid = re.search(r'\d+',url).group(0)
        else:
            wordid = '0'

        conn = self.CONN()
        cur = conn.cursor()
        cur.execute(
            "select 1 from baikeword_%s where urlmd5id  = %s",(ind,urlmd5id,))
        ret = cur.fetchone()

        if ret:
            cur.execute("""
                update baikeword_%s set title = %s,photo=%s,word=%s,explanation=%s,summarize=%s,
                full_text=%s,collect=%s,like_num=%s,share=%s,reference=%s,tag=%s,time=%s,author=%s,
                view=%s,now=%s,id=%s where urlmd5id=%s
                """,(ind,title,photo,word,explanation,
                     summarize,full_text,collect,like,share,
                     reference,tag,time,author,
                     view,now,wordid,urlmd5id)
            )
        else:
            cur.execute("""
            insert into baikeword_%s(urlmd5id,title,photo,word,explanation,summarize,full_text,collect,like_num,share,
            reference,tag,time,author,view,now,id)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            """,(ind,urlmd5id,title,photo,word,explanation,summarize,full_text,collect,like,share,reference,tag,time,author,view,now,wordid))

        conn.commit()
        cur.close()
        conn.close()
        #self.print_msg('finish '+url)
        #print urlmd5id
        #print str(ind)+'  '+str(wordid)
        global finish
        finish += 1
        self.cnt += 1

def main():
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    st = URL_START
    ed = URL_END
    thread_num = THREAD_NUM
    num = (ed-st)/thread_num
    i = 0
    j = st
    thread_l=[]
    while i < thread_num:
        thread_l.append(MultiScraper('thread_'+str(i),j,j+num))
        j += num
        i += 1
    for k in thread_l:
        k.start()
    while threading.activeCount() > 1:
        for k in thread_l:
            k.print_cnt()
            print k.url + "   maybe dying"
        time.sleep(30)
    print 'finish ' + str(finish) 
    print 'item_cnt' + str(item_cnt)
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    for k in thread_l:
        k.print_msg(str(k.cnt) + ' error ' + str(k.error))
if __name__ == '__main__':
    main()
