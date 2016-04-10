# -*- coding:utf8 -*-

import MySQLdb
import setting

MYSQL_HOST=setting.MYSQL_HOST
MYSQL_DBNAME=setting.MYSQL_DBNAME
MYSQL_USER=setting.MYSQL_USER
MYSQL_PASSWD=setting.MYSQL_PASSWD

def ConnMysql():
   return MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWD, db=MYSQL_DBNAME, charset='utf8')
