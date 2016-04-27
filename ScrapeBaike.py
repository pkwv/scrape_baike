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
import MyRequest
import ConnMysql
import requests

err_code = 'iso-8859-1'

class ScrapeBaike(threading.Thread):
    def __init__(self, thread_id, st, ed):
        super(ScrapeBaike, self).__init__()
        self.thread_id = thread_id
        self.st = st
        self.ed = ed
        self.success = 0
        self.error = 0
        self.f=open('log/'+str(thread_id)+'.txt','w')
        self.url=''
        self.web=''
        self.notuse=0
        self.use = 0
        self.proxy = ''
        self.error_page=[]
    def get_proxy(self):
        conn = ConnMysql.ConnMysql()
        cur = conn.cursor()
        cur.execute('select * from proxies limit 1')
        res = cur.fetchone()
        self.proxy = res[0][0]
        cur.execute('delete from proxies where url=%s',(self.proxy,))
        conn.commit()
        cur.close()
        conn.close()
    def print_msg(self, content):
        print str(self.thread_id) + ' ' + content
    
    def print_success_error(self):
        print '~~~~' + str(self.thread_id) + ' success ' + str(self.success) + ' error ' + str(self.error)

    def make_request(self, url, use = True):
        if not use:
            self.notuse += 1
        else:
            self.use += 1
        self.url = url
        return  MyRequest.MyRequest(url, use, self.thread_id)
 
    def get_unicode_text(self, res):
        if res.encoding.lower() == err_code:
            lst = requests.utils.get_encodings_from_content(res.text)
            if(len(lst)==0):
                return res.text.encode(err_code).decode('utf-8')
            else:
                return res.text.encode(err_code).decode(lst[0])
            #return res.text.encode(err_code).decode(requests.utils.get_encodings_from_content(res.text)[0])
        else:
            return res.text
    def check(self):
        if self.web == '':
            return False
        try:
            sel = etree.HTML(self.get_unicode_text(self.web))
        except:
            self.f.write(self.url+' '+self.web.url + ' error in check\n')
            #self.print_msg('here')
            return False
       
        #print item['url']
        word=self.link_list(sel.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()'))  #utf8
        if word=='':
            return False
        return True
        #self.print_msg(res.url + '  ' + word)
        #explanation=self.link_list(sel.xpath('string(//div[@class="lemma-summary"])'))   #utf8
        

    def run(self):
        i = self.st
        while i < self.ed:
            ''' just do it'''
            url = 'http://baike.baidu.com/view/' + str(i) + '.htm'
            ok = False
            req_num = 3
            #has = False
            for j in range(req_num):
                # the last request, i will not use proxy
                self.web = self.make_request(url, j!=req_num-1)
                # it must be error in baike
                #if 'baidu' not in self.web.url:# or '127.0.0.1' in self.web.url or 'baidu' not in self.web.url:
                #    if j!=req_num-1:
                #        has = True
                if self.check():
                    self.parse_item()
                    self.parse()
                    ok = True
                    break
            #if ok and has:
            #    self.f.write('rule is not right\n')
            if not ok:
                if self.web=='':
                    url_out = 'redirect'
                else :
                    url_out = self.web.url
                self.f.write(self.url + ' '+url_out+' error in url\n')
                self.error += 1
            i += 1
            if i%1000 == 0:
                self.print_msg(str(i))
                self.f.flush()
        print str(self.thread_id)+' is finished'

    def parse(self):
        #self.parse_item(res)
        # url do not contain 'error' 
        if 'subview' in self.web.url:
            sel = etree.HTML(self.get_unicode_text(self.web))
            suburl = sel.xpath('//ul[@class="polysemantList-wrapper cmn-clearfix"]//li/a/@href')
            for url in suburl:
                u = 'http://baike.baidu.com'+url
                ok = False
                req_num = 3
                for i in range(req_num):
                    # the last request, i will not use proxy
                    self.web = self.make_request(u,i!=req_num-1)
                    if self.check():
                        self.parse_item()
                        ok = True
                        break
                if not ok:
                    #self.add_error(url)
                    self.f.write(self.url + ' ' + self.web.url + ' error in suburl\n')
                    self.error += 1
        #self.parse_item(res)
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
        return ConnMysql.ConnMysql() 
    def parse_item(self):
        # res.url don't have 'error'
        #print self.get_unicode_text(res).encode('utf-8')
        try:
            sel = etree.HTML(self.get_unicode_text(self.web))
        except:
            self.f.write(self.url+' '+self.web.url + ' error in etree.HTML\n')
            self.error += 1
            #self.print_msg('here')
            return
        url = self.get_url(self.web.url)
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
        #self.print_msg(res.url + '  ' + word)
        explanation=self.link_list(sel.xpath('string(//div[@class="lemma-summary"])'))   #utf8
        if word == '':
            self.f.write(self.url+' '+self.web.url + ' no word' + '\n')
            self.error += 1
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
            if j<l2_len:
                dict[i]=l2[j]
            else:
                break
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
        ok = False
        while not ok:
            try:
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
                ok = True
            except:
                time.sleep(60*1)
        cur.close()
        conn.close()
        self.success += 1

#def main():
#    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#    st = URL_START
#    ed = URL_END
#    thread_num = THREAD_NUM
#    num = (ed-st)/thread_num
#    i = 0
#    j = st
#    thread_l=[]
#    while i < thread_num:
#        thread_l.append(MultiScraper('thread_'+str(i),j,j+num))
#        j += num
#        i += 1
#    for k in thread_l:
#        k.start()
#    for k in thread_l:
#        k.join()   
#    while threading.activeCount() > 1:
#        l = threading.enumerate()
#        for k in l:
#            print '&&&&****^^^' + k.getName()
#        time.sleep(30)
#    print 'finish ' + str(finish) 
#    print 'item_cnt' + str(item_cnt)
#    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#    for k in thread_l:
#        k.print_msg(str(k.cnt) + ' error ' + str(k.error))
#if __name__ == '__main__':
#    main()
