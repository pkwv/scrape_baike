# -*= coding:utf8 -*-

import MySQLdb
import MySQLdb.cursors
import ConnMysql
import user_agent
import requests
import random 
import time

err_code = 'ISO-8859-1'
def ToUnicode(text):
    return text.encode(err_code).decode(requests.utils.get_encodings_from_content(text)[0])

def DeleteProxy(ip):
    conn = ConnMysql.ConnMysql()
    cur = conn.cursor()
    cur.execute("delete from proxies where url = %s",(ip,))
    conn.commit()
    cur.close()
    conn.close()
    
    

def MyRequest(url, UseProxy = True,threadid = -1):
    cnt = 0
    num = 0
    tot = 0
    sleep = 0
    r = len(user_agent.USER_AGENTS)
    while True:
        if UseProxy:
            conn = ConnMysql.ConnMysql()
            cur = conn.cursor()
            cur.execute("select * from proxies limit 50")
            res = cur.fetchall()
            l = cur.rowcount
            cur.close()
            conn.close()
            lst = []
            for i in res:
                lst.append(i[0])
            random.shuffle(lst)
            #i = random.randint(0, l - 1)
            #proxies = {'http':res[i][0]}
            for i in lst:
                cnt += 1
                proxies = {'http':i}
                j = random.randint(0, r - 1)
                headers = {'user-agent':user_agent.USER_AGENTS[j]}
                try:
                    req = requests.get(url, headers=headers, proxies=proxies, timeout=(5.05,60))
                    if len(requests.utils.get_encodings_from_content(req.text)) == 0:
                        #tot += 1
                        DeleteProxy(i)
                        continue
                    if ('error' in req.url or '127.0.0.1' in req.url or 'baidu' not in req.url) and num < 3:
                    #if '127.0.0.1' in req.url and num < 1:
                        num += 1
                    #    DeleteProxy(i)
                        continue
                except requests.exceptions.RequestException as e:
                   # print e 
                    DeleteProxy(i)
                    continue
                #print url + ' cnt  ' + str(cnt)
                #if req.encoding == err_code:
                #    req.text = ToUnicode(req.text)
                return req
        else:
           
            j = random.randint(0, r - 1)
            headers = {'user-agent':user_agent.USER_AGENTS[j]}
            try:
                req = requests.get(url, headers=headers)
            except requests.exceptions.RequestException as e:
                if sleep > 0:
                    return ''
                sleep += 1
                n = 1
                print url+' maybe wrong  ',
                print e
                print str(threadid)+' sleep ' + str(n) + ' mimutes'
                time.sleep(60*n)
                #f=open('request_log.txt','wb')
                #f.write('not use proxy :' + e + '\n')
                #f.close()
                #print "not use proxy :" + e
                continue
            #if req.encoding == err_code:
            #    req.text = ToUnicode(req.text)
            return req
        time.sleep(10)
