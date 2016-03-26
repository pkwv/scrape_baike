# -*= coding:utf8 -*-

import MySQLdb
import MySQLdb.cursors
import ConnMysql
import user_agent
import requests
import random 

def MyRequest(url, UseProxy = True):
    cnt = 0
    while True:
        conn = ConnMysql.ConnMysql()
        cur = conn.cursor()
        cur.execute("select * from proxies")
        res = cur.fetchall()
        l = cur.rowcount
        cur.close()
        conn.close()
        lst = []
        for i in res:
            lst.append(i[0])
        random.shuffle(lst)
        r = len(user_agent.USER_AGENTS)
        if UseProxy:
            #i = random.randint(0, l - 1)
            #proxies = {'http':res[i][0]}
            for i in lst:
                cnt += 1
                proxies = {'http':i}
                j = random.randint(0, r - 1)
                headers = {'user-agent':user_agent.USER_AGENTS[j]}
                try:
                    req = requests.get(url, headers=headers, proxies=proxies, timeout=(3.05,60))
                except requests.exceptions.RequestException as e:
                   # print e 
                    conn = ConnMysql.ConnMysql()
                    cur = conn.cursor()
                    cur.execute("delete from proxies where url = %s",(i,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    continue
                print url + ' cnt  ' + str(cnt)
                return req
        else:
           
            j = random.randint(0, r - 1)
            headers = {'user-agent':user_agent.USER_AGENTS[j]}
            try:
                req = requests.get(url, headers=headers)
            except requests.exceptions.RequestException as e:
                print e
            return req
