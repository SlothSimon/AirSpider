#!/usr/bin/env python27
# -*- coding: utf-8 -*-

from ceair_spider import *

from time import clock
from time import sleep
import time
from insertToDB import *

while 1:
    clock()
    fout = open('ceair_log2.txt','a')
    today = time.strftime('%Y-%m-%d %H %M %S',time.localtime(time.time()))
    fout.write('%s the spider has been started.\n' % today)
    #hot_city = ['上海','北京']
    hot_city=['上海','北京','昆明','西安','广州','成都','杭州','青岛','深圳','太原','长沙']
    threads = []
    #打开数据库
    #conn, cursor = opendb('ceair')
    for i in range(0,len(hot_city)):
        for j in range(0, len(hot_city)):
            if i!=j:
                new_thread = ceair_thread(hot_city[i],hot_city[j], 0, 20)#conn,cursor,0,90)
                threads.append(new_thread)
    # new_thread = ceair_thread(hot_city[0],hot_city[1], 0, 10)#conn,cursor,0,90)
    # threads.append(new_thread)

    for athread in threads:
        athread.start()

    for athread in threads:
        athread.join()
        
    used_time = clock()
    print '总用时', used_time
    #关闭数据库
    #closedb(conn, cursor)
    
    fout.write('Finished. Time used:%s\n' % used_time)
    fout.close()
    if used_time <= 86400:
        sleep(86400-used_time)

