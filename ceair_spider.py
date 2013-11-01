# -*- coding: utf-8 -*-
import copy
import json
import time
import urllib
import urllib2

import MySQLdb
import requests

def writeErr(text,cause,date,dept,arr):
    err = open('err.txt','a')
    err.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'\n')
    err.write(date+dept+'->'+arr+'数据抓取失败。失败原因：'+cause+'\n')
    err.write('response如下：\n')
    err.write(text+'\n')
    err.close()

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
#    con = MySQLdb.connect(host='localhost', user='root',passwd='62093562',db='ceair',charset="utf8")
#    cursor = con.cursor()
    flights=[]

    url = 'http://easternmiles.ceair.com/booking/flight-search!doFlightSearch.shtml?rand=0.5428630779829127 HTTP/1.1'
    values = {'searchCond':'{"tripType":"OW","adtCount":"1","chdCount":"0","currency":"CNY","sortType":"t","segmentList":[{"deptCdTxt":"ä¸æµ·","deptCd":"DEPT","deptNation":"CN","deptRegion":"CN","deptCityCode":"null","arrCd":"ARR","arrCdTxt":"åäº¬","arrNation":"CN","arrRegion":"CN","arrCityCode":"null","deptDt":"DATE"}]}'}
    values['searchCond'] = values['searchCond'].replace('DEPT',str(dept)+'#')
    values['searchCond'] = values['searchCond'].replace('ARR',str(arr)+'#')
    save = {}
    save['searchCond']=values['searchCond']

    for i in range(ran):
        #url为request指向网址，values为需要post的数据
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()+sta*24*60*60+i*24*60*60))        
        #修改日期
        values['searchCond'] = save['searchCond']
        values['searchCond'] = values['searchCond'].replace('DATE',str(date))
        try:
            print "正在抓取"+date+"的机票信息..."
            #对values进行url编码
            data = urllib.urlencode(values)
            #建立一个request类型的对象
            req = urllib2.Request(url, data)
            #response为post后返回的内容
            response = urllib2.urlopen(req)
        
        #待完成#    应该增加重试的代码，重试一次后不成功再continue    
        except urllib2.HTTPError,e:
            print 'HTTPError:',e.code
            writeErr(e.read(),'HTTPError:'+e.code,date,dept,arr)
            continue
        except urllib2.URLError,e:
            print 'URLError,请检查网络。'
            print e.reason
            writeErr('无','URLError'+e.reason,date,dept,arr)
            continue
        except:
            print '错误，有可能未连入网络。'
            writeErr('无','打开网页失败',date,dept,arr)
            continue
        
        #读取为string类型
        temp = response.read()
        #去掉影响json解析的字符
        temp = temp[24:]
        try:
            #对json格式的数据进行解析
            text = json.loads(temp)
        except:
            print 'json解析失败！'
            writeErr(temp,'json解析失败',date,dept,arr)
            continue
        
        try:     
            #提取所需信息
            for a in range(len(text['tripItemList'][0]['airRoutingList'])):
                #某一航班
                site = text['tripItemList'][0]['airRoutingList'][a]
                flight=[]
                #航班号
                flight.append(site['flightList'][0]['flightNo'])
                #机型
                flight.append(site['flightList'][0]['acfamily'])
                #出发日期时间
                flight.append(site['flightList'][0]['deptTime'])
                #到达日期时间
                flight.append(site['flightList'][0]['arrTime'])
                
                #对价格一栏是否存在value进行判断，若没有则赋值为0
                if site['priceDisp']['lowest']:
                    flight.append(site['priceDisp']['lowest'])
                else:
                    flight.append(0)
                    
                #抓取日期    
                flight.append(time.strftime('%Y-%m-%d',time.localtime(time.time())))
                flight = tuple(flight)
                #测试#    输出观察用
                #print flight
                flights.append(flight)
        except:
            print '提取信息失败！'
            writeErr(temp,'提取信息失败',date,dept,arr)
            continue
        print '抓取成功'
        time.sleep(1) 
    return flights
            
ceair_spider('PEK','SHA',sta=2,ran=1)