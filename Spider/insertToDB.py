# -*- coding: utf-8 -*-
'''
Created on 2013-11-1
插入数据库
@author: simon
'''
import time

import MySQLdb

def opendb(db_name):
    conn = MySQLdb.connect(host='localhost', user='root',passwd='root',db=db_name,charset="utf8")
    cursor = conn.cursor()
    cursor.execute('set interactive_timeout=24*3600')
    return (conn,cursor)

def closedb(conn, cursor):
    cursor.close()
    conn.close()

def insertTomysql(flights):
    """
    用以插入mysql数据库
    flights = [(出发城市，到达城市，航班号，机型，出发日期，出发时间，价格，抓取日期)*n]
    """
    conn = MySQLdb.connect(host='localhost', user='root',passwd='root',db='ceair',charset="utf8")
    cursor = conn.cursor()
    try:      
        for flight in flights:
            try:
                cursor.execute('insert ignore into city (flight,deptcity,arrcity) values (%s, %s, %s)',[flight[2],flight[0],flight[1]])
                cursor.execute('insert ignore into departure (flight, type, deptDate, deptTime) values (%s, %s, %s, %s)',flight[2:6])
                cursor.execute('select id from departure where flight = %s and deptdate = %s',[flight[2],flight[4]])
                id = cursor.fetchone()[0]
                cursor.execute('insert ignore into `fetch` (price,fetchdate,deptID) values (%s, %s, %s)',[flight[6],flight[7],id])
                
            except:
                print '没有成功写入：'.decode('utf-8'),flight
                db_err(flight)
    
        conn.commit()
        print '成功写入数据库。'.decode('utf-8')
    except MySQLdb.Error,e:
        #错误回滚
        conn.rollback
        for flight in flights:
            db_err(flight)
        print "Error %d: %s" % (e.args[0],e.args[1])
    cursor.close()
    conn.close()
        
def db_err(err_record):
    today =  time.strftime('%Y-%m-%d',time.localtime(time.time()))
    fout = open('db_err_'+today+'.txt','a')
    for i in err_record:
        fout.write(str(i)+' ')
    fout.write('\n')
    fout.close()
