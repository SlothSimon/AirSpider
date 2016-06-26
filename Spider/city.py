#!/usr/bin/env python27
# -*- coding: utf-8 -*-
__author__ = 'simon'

# 城市代码可在该网址找到：http://www.carnoc.com/mhzl/jchzl/airport3code.htm
# 如有需要可以写爬虫自动抓取城市代码
citycode = {'北京':'BJS',#与cd代码不同，PEK
            '上海':'SHA',
            '广州':'CAN',
            '昆明':'KMG',
            '西安':'SIA',#与cd代码不同，XIY
            '成都':'CTU',
            '杭州':'HGH',
            '青岛':'TAO',
            '深圳':'SZX',
            '太原':'TYN',
            '长沙':'CSX'}

cd = {'北京':'PEK',
      '上海':'PVG',
      '广州':'CAN',
      '昆明':'KMG',
      '西安':'XIY',
      '成都':'CTU',
      '杭州':'HGH',
      '青岛':'TAO',
      '深圳':'SZX',
      '太原':'TYN',
      '长沙':'CSX'}


def get_citycode(city):
	"""
	Parameter:
		str: city, e.g.'北京'
	Return:
		str: citycode
	"""
	return citycode[city]

def get_cd(city):
	"""
	Parameter:
		str: city e.g. '北京'
	Return:
		str: cd e.g. 'PEK'
	"""
	return cd[city]
