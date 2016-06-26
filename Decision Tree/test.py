#!/usr/bin/env python27
# -*- coding: utf-8 -*-
__author__ = 'simon'

import treepredict
import datetime
import numpy as np
import time

class flightline:

	def __init__(self, dp='NULL', arr='NULL'):
		self.dpcity = dp
		self.arrcity = arr

		# key为flightid，item为flight类型的对象
		self.set_of_flights = {}

	def add_new(self, deptid,flightid, date, time, ftype):
		self.set_of_flights[deptid] = {'flightid': flightid,
		                               'date': date,
		                               'time': time,
		                               'ftype': ftype,
		                               'price': {}}

	def is_in_set(self, deptid):
		if deptid not in self.set_of_flights.keys():
			return False
		return True

	def add_price(self, deptid, ftdate, price, result):
		if type(ftdate) == str and (type(price) == str or type(price) == int):
			price = self.price_to_int(price)
			self.set_of_flights[deptid]['price'][ftdate] = (price, result)
		elif type(ftdate) == list and type(price) == list:
			if len(ftdate) != len(price):
				print 'ftdate和price长度不一致'
				return
			for i in range(len(ftdate)):
				price = self.price_to_int(price)
				self.set_of_flights[deptid]['price'][ftdate[i]] = (price[i],result)

	def get_deptid(self, flightid, date):
		for deptid in self.set_of_flights.keys():
			flight = self.set_of_flights[deptid]
			if flight['flightid'] == flightid and flight['date'] == date:
				return deptid
		return None

	def price_to_int(self, price):
		try:
			price = int(price)
		except:
			print '不是数字'
			return
		return price

	def get_flights(self):
		return copy.deepcopy(self.set_of_flights)

	def get_flights_by_dpdate(self, dpdate):
		flights = {}
		fl = self.set_of_flights
		for deptid in fl.keys():
			if fl[deptid]['date'] == dpdate:
				flights[deptid] = fl[deptid]
		return flights

	def get_flights_by_dptime(self, dptime):
		pass

	def get_flights_by_deptid(self, deptid):
		fl = self.set_of_flights
		return fl[deptid]


def bw_days(deptdate, fetchdate):
	"""计算日期间天数"""
	dd = deptdate.split('/')
	dpdate = datetime.date(int(dd[0]), int(dd[1]), int(dd[2]))
	fd = fetchdate.split('/')
	ftdate = datetime.date(int(fd[0]), int(fd[1]), int(fd[2]))
	return (dpdate-ftdate).days

def weekday(date):
	"""计算该天为周几"""
	dd = date.split('/')
	date = datetime.date(int(dd[0]), int(dd[1]), int(dd[2]))
	return date.weekday()

def weeks_before_dept(days):
	"""出发前第X周"""
	return days/7 + 1

def pre(points):
	"""返回的格式为{1:456,2:400,...}"""
        """填补空缺值，现采用方式是，在已有数据中，从距离起飞日期最近的一天开始填补。如距起飞第20天没有价格，则按第19天的价格补上。"""
        points = sorted(points, key=lambda x:x[0])
        x = []
        y = []
        z = []

        for p in points:
            x.append(p[0])
            y.append(p[1])
            z.append(p[2])

        day_empty = []
        try:
            y_max = max(y)
        except:
            pass

        for i in range(points[-1][0] - points[0][0] + 1):
                day = i + points[0][0]
                if day not in x:
                        x.insert(i, day)
                        y.insert(i, y[i-1])
                        z.insert(i, z[i-1])
                        day_empty.append((day, y[i], z[i]))

        points = {}
        for i in range(len(x)):
                points[x[i]]= (y[i], z[i])

        # print 'EMPTY_DAY:\n', day_empty
        # print 'EMPTY/ALL:', float(len(day_empty))/float(len(x))
        return points


def summary_stat(points):
	"""
	计算当前可知数据的总均值，标准差，总极差，总的最小值及其对应的距离起飞日期的天数
	最近一周的均值，最近一周的标准差，最近一周的极差
	"""
	days = points.keys()
	#print days
	days.reverse()
	#print 'After reverse:', days
	recent_day = min(days)
	#print "recent_day:", recent_day
	recent_week = recent_day/7
	n = 0
	recent_price = []
	while n <= 6 and n < len(days):
		cur_day = recent_day + n
		n = n + 1
		recent_price.append(points[cur_day][0])
	recent_price = np.array(recent_price)
	recent_mean = recent_price.mean()
	recent_std = recent_price.std()
	recent_range = recent_price.max() - recent_price.min()

	all_price = []
	for day in days:
		all_price.append(points[day][0])
	all_price = np.array(all_price)
	all_mean = all_price.mean()
	all_std = all_price.std()
	all_range = all_price.max() - all_price.min()

	min_price = all_price.min()
	min_day = all_price.argmin()
	if min_price == all_price.max():
		min_day = 0

	return {'recent_mean':recent_mean,
	        'recent_std':recent_std,
	        'recent_range':recent_range,
	        'all_mean':all_mean,
	        'all_std':all_std,
	        'all_range':all_range,
	        'min_price':min_price,
	        'min_day':min_day}




def get_data(flights):
	data = []

	for deptid in flights.keys():
		flight = flights[deptid]
		flightid = flight['flightid']
		ftype = flight['ftype']
		deptdate = flight['date']

		# 获得周几
		wkday = weekday(deptdate)
		time = flight['time']
		time = time.split(':')

		# 若起飞时间非常早或者非常晚，取为1，否则为0
		if int(time[0]) < 9 or int(time[0]) > 20:
			time = 1
		else:
			time = 0

		# 处理价格
		dd = flight['date']


		price = flight['price']

		points = []
		for ftdate in price.keys():
			days = bw_days(dd, ftdate)
			points.append((days, price[ftdate][0],price[ftdate][1]))

		points = pre(points)

		sorted(points, reverse=True)
		#统计结果
		results = summary_stat(points)

		#print points


		for day in points.keys():
			if points[day][1] == '1':
				result = 'buy'
			else:
				result = 'wait'
			#data.append((wkday, time, day, points[day][0], result))
			data.append((flightid, wkday, time, day, points[day][0], result))
			#将训练集写入txt文档

	return data

def writeintxt(filename, data):
	fout = open(filename,'w')
	for row in data:
		fout.write('%s %s %s %s %s %s %s\n' % row)
	fout.close()


fin = open('train_raw_flight_1.txt','r')
fl_lines = flightline('PEK', 'PVG')
lines = fin.readlines()
for line in lines:
	line = line.strip('\n')
	line = line.split(',')
	fl_lines.add_new(line[-1], line[0], line[4], line[-2], line[3])
fin.close()
fin = open('train_raw_price_1.txt','r')
lines = fin.readlines()
for line in lines:
	line = line.strip('\n')
	line = line.split(',')
	#print line
	fl_lines.add_price(line[0], line[1], line[2], line[3])

sta_time = time.clock()

#print fl_lines.get_flights_by_dpdate('2014/05/19')

#exit()

train_flights = {}
orig_date = datetime.date(2014, 2, 1)
for i in range(60):
	timedelta = datetime.timedelta(i)
	cur_date = orig_date + timedelta
	str_date = cur_date.strftime('%y/%m/%d')
	str_date = "20"+str_date
	new_flights = fl_lines.get_flights_by_dpdate(str_date)
	train_flights.update(new_flights)

#train_flights = fl_lines.get_flights_by_dpdate('2014/05/25')
#print train_flights
print '训练数据读入完成,用时', time.clock()

train_data = get_data(train_flights)
#writeintxt('train_data.txt',train_data)
flighttree = treepredict.buildtree(train_data, scoref=treepredict.giniimpurity)
#treepredict.drawtree(flighttree, 'test.jpg')
print '树训练完成，用时%s，数据%s条' %(time.clock(), len(train_data))

test_flights = {}
orig_date = datetime.date(2014, 5, 2)
for i in range(10):
	timedelta = datetime.timedelta(i)
	cur_date = orig_date + timedelta
	str_date = cur_date.strftime('%y/%m/%d')
	str_date = "20"+str_date
	new_flights = fl_lines.get_flights_by_dpdate(str_date)
	test_flights.update(new_flights)

test_data = get_data(test_flights)
#writeintxt('test_data.txt', test_data)
print '测试数据读入完成，用时', time.clock()

corr = 0.0
err_shouldwait = 0.0
err_shouldbuy = 0.0
for row in test_data:
	obs = row[:-1]
	pred = treepredict.classify(obs, flighttree)
	pred = pred.keys()[0]
	#print pred
	if pred == row[-1]:
		corr = corr + 1
	elif pred == 'wait':
		#print '实际为，价格%s，%s' % (row[-2], row[-1])
		err_shouldbuy = err_shouldbuy + 1
	else:
		#print '实际为，价格%s，%s' % (row[-2], row[-1])
		err_shouldwait = err_shouldwait + 1

size = float(len(test_data))
print "正确率：", float(corr)/size
print '错误情况：应当买却没买%s，应当等却买了%s。' % (err_shouldbuy/size, err_shouldwait/size)
print '预测%s个数据用时%s' % (len(test_data), time.clock())
print '总用时', time.clock()-sta_time

