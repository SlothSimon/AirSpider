#!/usr/bin/env python27
# -*- coding: utf-8 -*-

import copy
import json
import time
import urllib
import urllib2
import requests
from insertToDB import *
import thread
import threading
import random
from time import clock
import city
import socket

#socket.setdefaulttimeout(20)


def getproxy():
    """ 获取代理 """
    f = open('proxy.txt','r')
    text = f.read()
    f.close()
    p = text.split('\n')
    p = p[:-1]
    return p

proxy = getproxy()

def writeErr(text,cause,date,dept,arr):
    err = open('err.txt','a')
    err.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'\n')
    err.write(date+dept+'->'+arr+'数据抓取失败。失败原因：'+cause+'\n')
    err.write('response如下：\n')
    err.write(text+'\n\n')
    err.close()

# def openurl(opener, values, url, headers):
#     err = 0
#     while err < 2 and err >= 0:
#         try:
#             #对values进行url编码
#             data = urllib.urlencode(values)
#             #建立一个request类型的对象
#             req = urllib2.Request(url, data, headers=headers)
#             time.sleep(5)
#             #response为post后返回的内容
#             response = opener.open(req)
#             #获取response成功后将err标志改为-1
#             err = -1
            
#         #待完成：应该增加重试的代码，重试一次后不成功再continue#    
#         except urllib2.HTTPError,e:
#             print 'HTTPError:',e.code
#             #writeErr(e.read(),'HTTPError:'+e.code,date,dept,arr)
#             err = err + 1
#             continue
#         except urllib2.URLError,e:
#             print 'URLError,please check the net.\n'
#             print e.reason
#             #writeErr('无','URLError'+e.reason,date,dept,arr)
#             #上面这一行代码有问题，每次运行到这就报错。
#             err = err + 1
#             continue
#         except:
#             print "Error, it is possible that the computer doesn't connect to the Internet.\n"
#             #writeErr('无','打开网页失败',date,dept,arr)
#             err = err + 1
#             continue

#     if err >= 2:
#         return False
#     else:
#         return response


def ceair_spider(dept,arr,sta=0,ran=1):
    """ This function is used to achieve the flights' information on www.ceair.com.
        Parameters' info:
            sta: Date you want to start to achieve, e.g. input 0 when you want to start on tomorrow.
                range:[0:]
            ran: Range of date you want to achieve from the starting day, including the starting day.
                range:[1:]
            dept: Where the flight departures.
            arr: Where the flight departures.

        by simon
        2013.5.31
        """
    flights=[]
    deptcdtxt = dept
    arrcdtxt = arr

    dept = city.get_cd(dept)
    arr = city.get_cd(arr)

    deptcitycode = city.get_citycode(deptcdtxt)
    arrcitycode = city.get_citycode(arrcdtxt)

    #print deptcdtxt, arrcdtxt, deptcitycode, arrcitycode

    url = 'http://easternmiles.ceair.com/booking/flight-search!doFlightSearch.shtml?rand=0.4091873385477811'
    values = {'searchCond':'{"segmentList":[{"deptCdTxt":"DEPT-TXT","deptCd":"DEPT","deptNation":"CN","deptRegion":"CN","deptCityCode":"DEPT-CITYCODE","arrCd":"ARR","arrCdTxt":"ARR-TXT","arrNation":"CN","arrRegion":"CN","arrCityCode":"ARR-CITYCODE","deptDt":"DATE"}],"tripType":"OW","adtCount":"1","chdCount":"0","infCount":"0","currency":"CNY","sortType":"t"}'}
    values['searchCond'] = values['searchCond'].replace('DEPT-TXT', deptcdtxt)
    values['searchCond'] = values['searchCond'].replace('ARR-TXT', arrcdtxt)
    values['searchCond'] = values['searchCond'].replace('DEPT-CITYCODE', deptcitycode)
    values['searchCond'] = values['searchCond'].replace('ARR-CITYCODE', arrcitycode)
    values['searchCond'] = values['searchCond'].replace('DEPT', dept+'#')
    values['searchCond'] = values['searchCond'].replace('ARR', arr+'#')


    referer = 'http://easternmiles.ceair.com/flight/'+dept+'-'+arr+'-DATE_CNY.html'
    save = {}
    save['searchCond']=values['searchCond']
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
               'X-Requested-With':'XMLHttpRequest',
               'host':'easternmiles.ceair.com',
               'Connection':'keep-alive',
               'Origin':'http://easternmiles.ceair.com'}

    import cookielib
    cookie = cookielib.CookieJar()
    ck = urllib2.HTTPCookieProcessor(cookie)

    proxy_id = random.randint(0, len(proxy)-1)
    proxies = {'http': proxy[proxy_id]}
    handler = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(handler, ck, urllib2.HTTPHandler)

    sum_flights = 0


    
    for i in range(ran):
        #url为request指向网址，values为需要post的数据
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()+sta*24*60*60+i*24*60*60))
        date2 = time.strftime('%Y%m%d',time.localtime(time.time()+sta*24*60*60+i*24*60*60))        
        #修改日期
        values['searchCond'] = save['searchCond']
        values['searchCond'] = values['searchCond'].replace('DATE',str(date))
        headers['Referer'] = referer.replace('DATE', str(date2)[2:])
        print "正在抓取%s从%s至%s的机票信息...\n" %(date,dept,arr)

        #print values

        err = 0
        while err < 2 and err >= 0:
            try:
                #对values进行url编码
                data = urllib.urlencode(values)
                #建立一个request类型的对象
                req = urllib2.Request(url, data, headers=headers)
                time.sleep(5)
                #response为post后返回的内容
                response = opener.open(req)
                #获取response成功后将err标志改为-1
                err = -1
                
            #待完成：应该增加重试的代码，重试一次后不成功再continue#    
            except urllib2.HTTPError,e:
                print 'HTTPError:',e.code
                #writeErr(e.read(),'HTTPError:'+e.code,date,dept,arr)
                err = err + 1
                continue
            except urllib2.URLError,e:
                print 'URLError,please check the net.\n'
                print e.reason
                #writeErr('无','URLError'+e.reason,date,dept,arr)
                #上面这一行代码有问题，每次运行到这就报错。
                err = err + 1
                continue
            except err:
                print err
                print "Error, it is possible that the computer doesn't connect to the Internet.\n"
                writeErr('无','打开网页失败',date,dept,arr)
                err = err + 1
                continue
            
        #如果是因为两次尝试都失败而跳出循环则跳过这个起飞日期的爬取
        if err >= 2:
            continue
##        response = openurl(opener,values, url, headers)
##        if response == False:
##            continue
        
        #读取为string类型
        temp = response.read()
        response.close()
        opener.close()
        #去掉影响json解析的字符
        temp = temp[temp.find('{'):]
        try:
            #对json格式的数据进行解析
            text = json.loads(temp)
        except:
            print 'json解析失败！'.decode('utf-8')
            writeErr(temp,'json解析失败',date,dept,arr)
            continue
        
        try:
            #剔除没有航班的航线
            #print values
            #print temp
            if text['adtNum']!=0:
                
                #提取所需信息
                for a in range(len(text['tripItemList'][0]['airRoutingList'])):
                    #某一航班
                    site = text['tripItemList'][0]['airRoutingList'][a]
                    #预加入出发与到达城市
                    flight=[dept,arr]
                    if site['priceDisp']['lowest']:
                    #选择有票价的航班抓取
                        #航班号
                        flight.append(site['flightList'][0]['flightNo'])
                        #机型
                        flight.append(site['flightList'][0]['acfamily'])
                        #出发日期
                        flight.append(site['flightList'][0]['deptTime'][0:10])
                        #出发时间
                        flight.append(site['flightList'][0]['deptTime'][11:])
                        #最低价格
                        flight.append(site['priceDisp']['lowest'])                        
                        #抓取日期    
                        flight.append(time.strftime('%Y-%m-%d',time.localtime(time.time())))
                        flight = tuple(flight)
                        #测试#    输出观察用
                        #print flight
                        flights.append(flight)
                    else:
                        continue
            else:
                print '没能抓取%s从%s至%s的机票信息\n'%(date, dept, arr)
                print text
                #print text
                continue
        except:
            print '提取信息失败！'
            writeErr(temp,'提取信息失败',date,dept,arr)
            continue
        num_flights = len(flights)
        sum_flights = sum_flights + num_flights
        # print flights

        for item in cookie:
            print item.name+":"+item.value
        print '%s从%s至%s的机票信息抓取成功,共%s条。\n'%(date, dept, arr, num_flights)
	print '从%s至%s的机票信息共%s条。'%(dept, arr, sum_flights)
    return flights

class ceair_thread(threading.Thread):

    def __init__(self,dept,arr,sta=0,ran=1):
        threading.Thread.__init__(self)
        self.dept = dept
        self.arr = arr
        self.sta = sta
        self.ran = ran


    def run(self):
		start = clock()
		flights = ceair_spider(self.dept,self.arr,self.sta,self.ran)
		#print len(flights)
		print '线程%s-->%s用时%s\n' %(self.dept, self.arr, clock()-start)

 
##conn, cursor = opendb('ceair')
#flights = ceair_spider('PEK','CAN',0,5)
#print flights
##insertTomysql(flights, conn, cursor)
##closedb(conn, cursor)

##
##clock()
##hot_city=['SHA','PVG','PEK','KMG','XIY','CAN','CTU','HGH','TAO','SZX','TYN','CSX']
##threads = []
##for i in range(0,len(hot_city)):
##    for j in range(0,len(hot_city)):
##        if i!=j:
##            new_thread = ceair_thread(hot_city[i],hot_city[j],0,90)
##            threads.append(new_thread)
##            #ceair_spider(hot_city[i],hot_city[j],sta=0,ran=2)
##            #insertTomysql(ceair_spider(hot_city[i],hot_city[j],sta=0,ran=90),'ceair')
##
##for athread in threads:
##    athread.start()
##
##for athread in threads:S
##    athread.join()
##
##print '总用时'.decode('utf-8'), clock()
        

