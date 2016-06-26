# -*- coding: utf-8 -*-
"""
该抓取代理的爬虫借用自网上开源代码，地址为
http://f.dataguru.cn/thread-54108-1-1.html
对提取信息的方法略作修改。

"""



import urllib2
import re
import sys
import chardet
import threading
import time
from pyquery  import PyQuery as pq
#reload(sys)
#sys.setdefaultencoding('utf-8') 

rawProxyList = []
checkedProxyList = []

#八个目标网站
targets = ['http://pachong.org/area/short/name/ve.html',
            'http://pachong.org/area/short/name/us.html',
            'http://pachong.org/area/city/name/%E5%A4%A9%E6%B4%A5.html',
            'http://pachong.org/area/city/name/%E5%90%88%E8%82%A5.html',
            'http://pachong.org/area/city/name/%E5%B9%BF%E5%B7%9E.html',
           'http://pachong.org/area/city/name/%E4%B8%8A%E6%B5%B7.html',
           'http://pachong.org/area/city/name/%E5%8C%97%E4%BA%AC.html',
           'http://pachong.org/area/city/name/%E4%B8%AD%E5%9B%BD.html',
           'http://pachong.org/area/city/name/%E6%AD%A6%E6%B1%89.html',
           'http://pachong.org/area/city/name/%E9%95%BF%E6%B2%BB.html'
           ]
##targets = ['http://pachong.org/area/city/name/%E5%A4%A9%E6%B4%A5.html']


#获取代理的类
class ProxyGet(threading.Thread):
    def __init__(self,target):
        threading.Thread.__init__(self)
        self.target = target
        
    def getProxy(self):
        print "目标网站： " + self.target
        req = urllib2.urlopen(self.target)
        result = req.read()
        #print chardet.detect(result)
        main = pq(result)
        for i in range(main('tbody')('tr').size()):
            if main('tr').eq(i+1).find('td').eq(4).text() != 'transparent':
                ip = main('tr').eq(i+1).find('td').eq(1).text()
                port = main('tr').eq(i+1).find('td').eq(2).text()
                address = main('tr').eq(i+1).find('td').eq(3).text()
                proxy = [ip,port,address]
                #print proxy
                rawProxyList.append(proxy)
            
    def run(self):
        self.getProxy()       
        
        
#检验代理的类    
class ProxyCheck(threading.Thread):
    def __init__(self,proxyList):
        threading.Thread.__init__(self)
        self.proxyList = proxyList
        self.timeout = 5
        self.testUrl = ["http://easternmiles.ceair.com/flight/"]
        self.testStr = ["10009470"]
        self.pos = {0:-1}
        
    def checkProxy(self):
        cookies = urllib2.HTTPCookieProcessor()
        for proxy in self.proxyList:
            proxyHandler = urllib2.ProxyHandler({"http" : r'http://%s:%s' %(proxy[0],proxy[1])})  
            #print r'http://%s:%s' %(proxy[0],proxy[1])
            opener = urllib2.build_opener(cookies,proxyHandler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1')]
            #urllib2.install_opener(opener)
            t1 = time.time()
            
            try:
                for i in range(len(self.testUrl)):
                    #req = urllib2.urlopen("http://www.baidu.com", timeout=self.timeout)
                    req = opener.open(self.testUrl[i], timeout=self.timeout)
                    #print "urlopen is ok...."
                    result = req.read()
                    #print "read html...."
                    timeused = time.time() - t1
                    self.pos[i] = result.find(self.testStr[i])
                    #print "pos is %s" %self.pos
                
                if (self.pos[0] > -1):
                    checkedProxyList.append((proxy[0],proxy[1],proxy[2],timeused))
                    #print "ok ip: %s %s %s %s" %(proxy[0],proxy[1],proxy[2],timeused)
                else:
                    continue
                
            except Exception,e:
                print "出错".decode('utf-8')
                print e.message
                continue
                       
    def sort(self):
        sorted(checkedProxyList,cmp=lambda x,y:cmp(x[3],y[3]))
                 
    def run(self):
        self.checkProxy()
        self.sort()
                
if __name__ == "__main__":
    getThreads = []
    checkThreads = []
    
    #对每个目标网站开启一个线程负责抓取代理
    for i in range(len(targets)):
        t = ProxyGet(targets[i])
        getThreads.append(t)
        
    for i in range(len(getThreads)):
        getThreads[i].start()
        
    for i in range(len(getThreads)):
        getThreads[i].join()        
        
    print ".......................总共抓取了%s个代理......................." %len(rawProxyList)   
    
    
    #开启20个线程负责校验，将抓取到的代理分成20份，每个线程校验一份
    for i in range(20):
        t = ProxyCheck(rawProxyList[((len(rawProxyList)+19)/20) * i:((len(rawProxyList)+19)/20) * (i+1)])
        checkThreads.append(t)
    
    for i in range(len(checkThreads)):
        checkThreads[i].start()
        
    
    for i in range(len(checkThreads)):
        checkThreads[i].join()
        
     
    print ".......................总共有%s个代理通过校验......................." %len(checkedProxyList)    
        
    #持久化    
    f= open("proxy.txt",'w+')
    for proxy in checkedProxyList:
        print "checked proxy is: %s:%s\t%s\t%s\n" %(proxy[0],proxy[1],proxy[2],proxy[3])
        f.write("%s:%s\n"%(proxy[0],proxy[1]))
    f.close()        
