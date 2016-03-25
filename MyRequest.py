# -*= coding:utf8 -*-

import MySQLdb
import MySQLdb.cursors
import ConnMysql
import user_agent
import requests
import random 

def MyRequest(url, UseProxy = True):
    conn = ConnMysql.ConnMysql()
    cur = conn.cursor()
    cur.execute("select * from proxies")
    res = cur.fetchall()
    l = cur.rowcount
    cur.close()
    conn.close()
    r = len(user_agent.USER_AGENTS)
    cnt = 0
    while True:
        cnt += 1
        if UseProxy:
            i = random.randint(0, l - 1)
            proxies = {'http':res[i][0]}
        j = random.randint(0, r - 1)
        headers = {'user-agent':user_agent.USER_AGENTS[j]}
        try:
            if UseProxy:
                #print headers
                #print proxies
                req = requests.get(url, headers=headers, proxies=proxies, timeout=(3.05,27))
            else:
                req = requests.get(url,headers=headers)
        except requests.exceptions.RequestException as e:
           # print e 
            conn = ConnMysql.ConnMysql()
            cur = conn.cursor()
            if UseProxy:
                cur.execute("delete from proxies where url = %s",(res[i],))
            conn.commit()
            cur.close()
            conn.close()
            continue
        print url + ' cnt  ' + str(cnt)
        return req

