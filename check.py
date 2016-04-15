# coding:utf-8

import ConnMysql
import MySQLdb
import MySQLdb.cursors
import codecs
import sys
#f = codecs.open('out.txt','w','utf-8')

def calc():
    conn = ConnMysql.ConnMysql()
    cur = conn.cursor()
    cnt = 0
    for i in range(10):
        cur.execute("select count(*) from baikeword_%s where word != '' and explanation != ''",(i,))
        res = cur.fetchone()
        print 'baikeword_'+str(i) + ' has ' + str(res) + ' papers'
        cnt += res[0]
        #while res:
        #   if res != '':
        #       cnt = cnt +1 
        #       if cnt % 100 == 0:
        #           print 'baikeword_'+str(i)+'   '+str(cnt)
        #   res = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    print cnt

def check_one():
    conn = ConnMysql.ConnMysql()
    cur = conn.cursor()
    cur.execute("select word,id from baikeword_2 limit 200")
    res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    code = sys.getfilesystemencoding()
    for i in res:
        #print i[1]
        if i[1] == '3280544':
 #           f.write(i[0])
            print i[0]
            print type(i[0])
            print code
            print i[0].encode(code)

if __name__ == "__main__":
    check_one()
    #calc()
