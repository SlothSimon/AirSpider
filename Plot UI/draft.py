#!/usr/bin/env python27
# -*- coding: gbk -*-
__author__ = 'simon'

import wx
import wx.calendar
import os
import datetime
import copy
import sys
import random

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib import pyplot as plt
import numpy as np

class flightline:

	def __init__(self, dp='NULL', arr='NULL'):
		self.dpcity = dp
		self.arrcity = arr

		# keyΪflightid��itemΪflight���͵Ķ���
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

	def add_price(self, deptid, ftdate, price):
		if type(ftdate) == str and (type(price) == str or type(price) == int):
			price = self.price_to_int(price)
			self.set_of_flights[deptid]['price'][ftdate] = price
		elif type(ftdate) == list and type(price) == list:
			if len(ftdate) != len(price):
				dlg = wx.MessageDialog(self, "The num of price is not same with the num of fetchdate",
				                       'Error!',
				                       wx.OK)
				dlg.ShowModal()
				dlg.Destroy()
				return
			for i in range(len(ftdate)):
				price = self.price_to_int(price)
				self.set_of_flights[deptid]['price'][ftdate[i]] = price[i]

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
			dlg = wx.MessageDialog(self,"The price is not a number!",
			                       'Error!',
			                       wx.OK)
			dlg.ShowModal()
			dlg.Destroy()
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

class myquery(wx.Panel):

	def __init__(self, parent=None):
		wx.Panel.__init__(self, parent, -1)

		# ���ݳ�Ա
		self.fl_lines = []

		## ���Ԫ��
		# ��ѡ��
		#deptcity
		self.ch_dpcity = wx.Choice(self, -1, style=wx.CB_SORT, name='deptcity')
		self.Bind(wx.EVT_CHOICE, self.OnChangeCH, self.ch_dpcity)
		#arrcity
		self.ch_arrcity = wx.Choice(self, -1, style=wx.CB_SORT, name='arrcity')
		self.Bind(wx.EVT_CHOICE, self.OnChangeCH, self.ch_arrcity)

		# ʵʱ��ѯ�Ƿ������ѡ�ĺ��ߣ���ʾ��̬�ı�
		self.tt_state = wx.StaticText(self, -1, "")
		self.tt_state.SetForegroundColour('red')

		# �������������������ڡ�ץȡ���ڣ���ѡ��

		# �����ؼ�
		self.calendar = wx.calendar.CalendarCtrl(self, -1, date=wx.DateTime().Today(),
		                                         style=wx.calendar.CAL_SHOW_HOLIDAYS | wx.calendar.CAL_SHOW_SURROUNDING_WEEKS | wx.calendar.CAL_MONDAY_FIRST)
		self.Bind(wx.calendar.EVT_CALENDAR_DAY, self.OnChangeCalendar, self.calendar)

		# # search button
		# self.bt_search = wx.Button(self, -1, "Search", name='bt_search')
		# self.Bind(wx.EVT_BUTTON, self.Search, self.bt_search)

		# �����б�
		self.lc_flight = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.LC_SORT_ASCENDING, name='flight')
		self.lc_flight.InsertColumn(0, '�����', width=60)
		self.lc_flight.InsertColumn(1, '����', width=50)
		self.lc_flight.InsertColumn(2, '���ʱ��')
		self.lc_flight.InsertColumn(3, 'deptID', width=0)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDoubleClick_lc_flight, self.lc_flight)

		#ѡ��ĺ����б�
		self.lc_choice = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.LC_SORT_ASCENDING)
		self.lc_choice.InsertColumn(0, '�����', width=60)
		self.lc_choice.InsertColumn(1, '��������')
		self.lc_choice.InsertColumn(2, '�������')
		self.lc_choice.InsertColumn(3, '����', width=50)
		self.lc_choice.InsertColumn(4, '�������')
		self.lc_choice.InsertColumn(5, '���ʱ��')
		self.lc_choice.InsertColumn(6, 'deptID', width=0)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDoubleClick_lc_choice, self.lc_choice)

		#��ͼ��ť
		self.bt_draw = wx.Button(self, -1, '��ͼ')
		self.bt_draw.SetDefault()
		self.Bind(wx.EVT_BUTTON, self.OnClickButton_draw, self.bt_draw)

		#���ѡ�ť
		self.bt_clearall = wx.Button(self, -1, '����б�')
		self.bt_clearall.SetDefault()
		self.Bind(wx.EVT_BUTTON, self.OnClickButton_clearall, self.bt_clearall)

		#��ջ�����ť
		self.bt_clear_canvas = wx.Button(self, -1, '��ջ���')
		self.bt_clear_canvas.SetDefault()
		self.Bind(wx.EVT_BUTTON, self.OnClickButton_clear_canvas, self.bt_clear_canvas)

		# ���ڲ�����
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.v1 = wx.BoxSizer(wx.VERTICAL)
		self.v2 = wx.BoxSizer(wx.VERTICAL)
		v1 = self.v1
		v2 = self.v2
		v1.AddMany([self.ch_dpcity, self.ch_arrcity, self.tt_state])

		v2.AddMany([self.calendar])

		self.h1 = wx.BoxSizer(wx.HORIZONTAL)
		h1 = self.h1
		h1.AddMany([v1, v2])
		self.sizer.AddMany([h1, self.lc_flight, self.lc_choice, self.bt_draw, self.bt_clearall, self.bt_clear_canvas])
		# self.sizer.Add(h1, proportion=0, border=2, flag=wx.ALL)
		# self.sizer.Add(self.lc_flight, proportion=0, border=2, flag=wx.ALL | wx.SHAPED)
		self.SetSizer(self.sizer)

	def add_city(self, fl_lines):
		"""fl_lines should be a list like [('PEK','SHA'),('CAN','PEK'),...]"""
		deptcity = []
		arrcity = []
		for line in fl_lines:
			if line not in self.fl_lines:
				deptcity.append(line[0].upper())
				arrcity.append(line[1].upper())
				self.fl_lines.append(line)
		if deptcity != []:
			self.ch_dpcity.AppendItems(deptcity)
		if arrcity != []:
			self.ch_arrcity.AppendItems(arrcity)

	def clear_city(self):
		self.ch_dpcity.Clear()
		self.ch_arrcity.Clear()
		self.fl_lines = []

	def OnChangeCH(self, evt):
		fromcity = self.ch_dpcity.GetStringSelection()
		tocity = self.ch_arrcity.GetStringSelection()
		if (fromcity, tocity) not in self.fl_lines:
			self.tt_state.SetLabel("û���������ߡ�")
		else:
			self.tt_state.SetLabel("")

	def OnChangeCalendar(self, evt):

		self.lc_flight.DeleteAllItems()
		dp = self.ch_dpcity.GetCurrentSelection()
		arr = self.ch_arrcity.GetCurrentSelection()
		if dp == wx.NOT_FOUND or arr == wx.NOT_FOUND:
			return
		dp = self.ch_dpcity.GetString(dp)
		arr = self.ch_arrcity.GetString(arr)
		d = self.calendar.GetDate().FormatDate()
		d = d.split('/')
		# if d[1][0] == '0':
		# 	d[1] = d[1][1]
		# if d[0][0] == '0':
		# 	d[0] = d[0][1]
		deptdate = '20'+d[2]+'/'+d[0]+'/'+d[1]
		flights = self.get_flights(dp, arr, deptdate)

		# flight = [flightid, ftype, time, deptid]
		lc = self.lc_flight
		for flight in flights:
			index = lc.InsertStringItem(sys.maxint, str(flight[0]))
			lc.SetStringItem(index, 1, str(flight[1]))
			lc.SetStringItem(index, 2, str(flight[2]))
			lc.SetStringItem(index, 3, str(flight[3]))

	def get_flights(self, dpcity, arrcity, deptdate):
		myline = self.GetParent().GetParent().fl_lines[(dpcity, arrcity)]
		fl = myline.get_flights_by_dpdate(deptdate)
		flights = []
		for deptid in fl.keys():
			flights.append([fl[deptid]['flightid'],
		                    fl[deptid]['ftype'],
		                    fl[deptid]['time'],
		                    deptid])
		return flights

	def OnDoubleClick_lc_flight(self, evt):
		dp = self.ch_dpcity.GetCurrentSelection()
		arr = self.ch_arrcity.GetCurrentSelection()
		dp = self.ch_dpcity.GetString(dp)
		arr = self.ch_arrcity.GetString(arr)

		myline = self.GetParent().GetParent().fl_lines[(dp, arr)]
		lc = self.lc_flight
		deptid = lc.GetItem(lc.GetFirstSelected(), 3).GetText()
		fl = myline.get_flights_by_deptid(deptid)
		dd = fl['date']
		dt = fl['time']
		flightid = fl['flightid']
		ftype = fl['ftype']

		lc = self.lc_choice
		index = lc.InsertStringItem(sys.maxint, str(flightid))
		lc.SetStringItem(index, 1, str(dp))
		lc.SetStringItem(index, 2, str(arr))
		lc.SetStringItem(index, 3, str(ftype))
		lc.SetStringItem(index, 4, str(dd))
		lc.SetStringItem(index, 5, str(dt))
		lc.SetStringItem(index, 6, str(deptid))

	def OnDoubleClick_lc_choice(self, evt):
		lc = self.lc_choice
		lc.DeleteItem(lc.GetFirstSelected())

	def OnClickButton_clearall(self, evt):
		lc = self.lc_choice
		lc.DeleteAllItems()

	def OnClickButton_clear_canvas(self, evt):
		self.GetParent().GetParent().myplot.clear(evt)

	def OnClickButton_draw(self, evt):
		lc = self.lc_choice
		for i in range(lc.GetItemCount()):
			dp = lc.GetItem(i, 1).GetText()
			arr = lc.GetItem(i, 2).GetText()
			deptid = lc.GetItem(i, 6).GetText()
			myline = self.GetParent().GetParent().fl_lines[(dp, arr)]
			fl = myline.get_flights_by_deptid(deptid)

			dd = fl['date']

			# str-->date
			dd = dd.split('/')
			deptdate = datetime.date(int(dd[0]), int(dd[1]), int(dd[2]))
			price = fl['price']

			points = []
			for ftdate in price.keys():
				ff = ftdate.split('/')
				fetchdate = datetime.date(int(ff[0]), int(ff[1]), int(ff[2]))
				days = (deptdate-fetchdate).days
				points.append((days, price[ftdate]))

			self.GetParent().GetParent().myplot.draw(points, fl['date'])



class myplot(wx.Panel):

	def __init__(self, parent=None):
		wx.Panel.__init__(self, parent, -1)

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.p_set = []

		self.figure = matplotlib.figure.Figure(figsize=(5,4))
		self.axes_normal = self.figure.add_subplot(111)
		self.axes_1diff = self.figure.add_subplot(312)
		self.axes_2diff = self.figure.add_subplot(313)

		self.setaxes(self.axes_normal)
		self.setaxes(self.axes_1diff)
		self.setaxes(self.axes_2diff)

		self.axes_1diff.set_visible(False)
		self.axes_2diff.set_visible(False)

		self.axes_normal.set_title('General')
		self.axes_1diff.set_title('1-diff')
		self.axes_2diff.set_title('2-diff')

		self.canvas = FigureCanvas(self, -1, self.figure)
		self.canvas.mpl_connect('pick_event', self.OnPick)
		self.canvas.mpl_connect('motion_notify_event', self.on_move)

		v1 = wx.BoxSizer(wx.VERTICAL)

		#static text: x,y
		self.tt_xy = wx.StaticText(self, -1, "")
		v1.Add(self.tt_xy, proportion=0, border=4, flag=wx.ALL)

		#multi choices boxes for point or line
		self.clb_style = wx.CheckListBox(self, -1,
		                             choices = ['Line', 'Point', 'legend'],
		                             name = 'style')
		self.Bind(wx.EVT_CHECKLISTBOX, self.OnChangeStyle, self.clb_style)
		h1 = wx.BoxSizer(wx.HORIZONTAL)
		h1.Add(self.clb_style, proportion=0, border=4, flag=wx.ALL)

		#various types of graphs
		self.clb_type = wx.CheckListBox(self, -1,
		                                choices = ['None', '1-diff', '2-diff',],
		                                name = 'type')
		self.Bind(wx.EVT_CHECKLISTBOX, self.OnChangeType, self.clb_type)
		h1.Add(self.clb_type, proportion=0, flag=wx.ALL)

		self.cb_xaxis = wx.CheckBox(self, label = 'Days as the x_axis')
		v1.Add(self.cb_xaxis, proportion=0, border=4, flag=wx.ALL)

		h1.Add(v1, proportion=0, flag=wx.ALL)
		self.sizer.Add(self.canvas, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)
		self.sizer.Add(h1, proportion=0, flag=wx.ALL)

		self.SetSizer(self.sizer)

	def setaxes(self, axes):
		axes.autoscale(False)
		axes.set_xlabel("days")
		axes.set_ylim(0)
		axes.set_xlim(0)
		axes.set_yticks(range(0,1500,100))

	def OnChangeType(self, evt):
		items = self.clb_type.GetChecked()
		axes = []
		if 0 in items:
		    axes.append(self.axes_normal)
		else:
		    self.axes_normal.set_visible(False)
		if 1 in items:
		    axes.append(self.axes_1diff)
		else:
		    self.axes_1diff.set_visible(False)
		if 2 in items:
		    axes.append(self.axes_2diff)
		else:
		    self.axes_2diff.set_visible(False)

		n = len(items)
		for i in range(n):
		    axes[i].change_geometry(n,1,i)
		    axes[i].set_visible(True)

		self.figure.subplots_adjust(hspace = 1)
		self.canvas.draw()
		self.canvas.mpl_connect('pick_event', self.OnPick)

	def OnChangeStyle(self, evt):
		if evt.GetInt() == 2:
			if self.clb_style.IsChecked(2):
				self.legend()
			else:
				self.unlegend()
			return

		self.figure.set_canvas(self.canvas)
		self.axes_normal.clear()
		self.axes_1diff.clear()
		self.axes_2diff.clear()
		self.canvas.draw()

		for row in self.p_set:
			self.draw(row[0], row[1])

	def highlight(self, target):
		"""���ƶ���������ʵʩ����"""
		need_redraw = False
		if target is None:
			# ��û���ƶ�������һ�����ߣ���ԭ����
			for line in self.axes_normal.lines:
				line.set_alpha(1.0)
				if line.get_linewidth() != 2.0:
					line.set_linewidth(2.0)
					need_redraw = True
		else:
			# ���ƶ��������ϣ����޸��߶δ�ϸ��͸����
			for line in self.axes_normal.lines:
				lw = 5 if line is target else 1
				if line.get_linewidth() != lw:
					line.set_linewidth(lw)
					need_redraw = True
				alpha = 1.0 if lw == 5 else 0.3
				line.set_alpha(alpha)

		if need_redraw:
			# ������һ���ߵ����Է����ı䣬�ڻ���idleʱ�����ػ�
			self.figure.canvas.draw_idle()

	def on_move(self, evt):
		"""��������ƶ��¼�����������"""

		ax = self.axes_normal
		# �����޲����ͼ�ϵ�����һ�����ߣ��ж����Ƿ��ڵ�ѡ��Χ�ڣ����������
		for line in ax.lines:
			if line.contains(evt)[0]:
				self.highlight(line)
				label = line.get_label()
				self.tt_xy.Label = '�������ڣ�' + label
				break
		else:
			self.highlight(None)

	def OnPick(self, evt):
		label = evt.artist.get_label()
		# xdata, ydata = evt.artist.get_data()
		# x, y = 0, 0
		# mx = evt.mouseevent.xdata
		# my = evt.mouseevent.ydata
		# mind = sys.maxint
		# for i in range(len(xdata)):
		# 	d = (mx-xdata[i])*(mx-xdata[i])+(my-ydata[i])*(my-ydata[i])
		# 	if d < mind:
		# 		mind = d
		# 		x = xdata[i]
		# 		y = ydata[i]

		# ������ʾΪ��һ�����֣�����ע�͵����в�֪������޸�Ϊ��������Ԥ������matplotlib���õ����ں���
		self.tt_xy.Label = '�������ڣ�' + label #+ ',' + str(x)+","+str(y)

	def draw(self, points, label=None):
		axes = []

		#���ȱֵ
		print 'Flight:', label
		points = self.pre(points)
		#�����쳣ֵ
		points = self.remove_abnormal_price(points)

		#����ѡ���ͼ��������ͼ
		if self.clb_type.IsChecked(0):
			self.draw_normal(points, label)
			axes.append(self.axes_normal)
		else:
			self.axes_normal.set_visible(False)
		if self.clb_type.IsChecked(1):
			self.draw_diff(points, 1, label, self.axes_1diff)
			axes.append(self.axes_1diff)
		else:
			self.axes_1diff.set_visible(False)
		if self.clb_type.IsChecked(2):
			self.draw_diff(points, 2, label, self.axes_2diff)
			axes.append(self.axes_2diff)
		else:
			self.axes_2diff.set_visible(False)

		n = len(axes)
		for i in range(n):
			axes[i].change_geometry(n, 1, i+1)
			axes[i].set_visible(True)

		self.canvas.draw()


	def draw_diff(self, points, n, label=None, axes=None):
		if axes == None:
		    axes = self.axes_1diff

		points = self.diff(points,n)
		self.draw_normal(points,label,axes)

	def diff(self, points, n):
		"""�Ե���в�ִ���"""
		points = sorted(points, key=lambda x:x[0])
		new_p = []
		for i in range(len(points)-1):
		    new_p.append((points[i][0],points[i][1]-points[i+1][1]))
		if n == 1:
		    return new_p
		else:
		    return self.diff(new_p,n-1)

	def pre(self, points):
		"""���ȱֵ���ֲ��÷�ʽ�ǣ������������У��Ӿ���������������һ�쿪ʼ��������ɵ�20��û�м۸��򰴵�19��ļ۸��ϡ�"""
		points = sorted(points, key=lambda x:x[0])
		x = []
		y = []

		for p in points:
		    x.append(p[0])
		    y.append(p[1])

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
				day_empty.append((day, y[i]))

		points = []
		for i in range(len(x)):
			points.append((x[i], y[i]))

		print 'EMPTY_DAY:\n', day_empty
		print 'EMPTY/ALL:', float(len(day_empty))/float(len(x))
		return points

	def remove_abnormal_price(self, points):
		"""
		�����쳣ֵ�������ƣ�Ŀǰ�ú���ֻ�Ǹ�Ϊ�˱������Ϻ���ȫ��Ʊ��δ������������

		"""
		minday = points[0][0]
		for i in range(len(points)):
			day = i + minday
			if points[i][1] > 1130:
				points[i] = (day, 1130)
		return points

	def draw_normal(self, points, label=None, axes=None):

		if axes == None:
			axes = self.axes_normal

		if [points, label] not in self.p_set:
			self.p_set.append([points, label])
		x = []
		y = []

		for point in points:
			x.append(point[0])
			y.append(point[1])

		if self.cb_xaxis.IsChecked() == False:
			dd = label.split('/')
			deptdate = datetime.datetime(int(dd[0]), int(dd[1]), int(dd[2]), 1, 0, 0)
			maxday = max(x)
			minday = min(x)
			start_date = deptdate - datetime.timedelta(days=maxday)
			end_date = deptdate - datetime.timedelta(days=minday - 1)
			delta = datetime.timedelta(hours=24)
			datecounts = matplotlib.dates.drange(start_date, end_date, delta)
			y.reverse()

		color = "#"
		for i in range(6):
			color += str(random.randint(0, 9))

		# try:
		if self.clb_style.IsChecked(0):
			if self.cb_xaxis.IsChecked() == True:
				axes.plot(x, y, 'm-', picker=8.0, label=label, linewidth=1, color=str(color))
			else:
				axes.plot_date(datecounts, y, 'm-', picker=8.0, label=label, linewidth=1, color=str(color))
			for line in axes.get_lines():
				line.set_lw(2)
		if self.clb_style.IsChecked(1):
			if self.cb_xaxis.IsChecked() == True:
				axes.plot(x, y, picker=5, label=label, color=color)
			else:
				axes.plot_date(datecounts, y, picker=5, label=label, color=color)

		if self.cb_xaxis.IsChecked() == False:
			axes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d') )
			axes.fmt_xdata = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')
			self.figure.autofmt_xdate()

		self.setup()
		# except:
		# 	pass

	def clear(self, evt):
		self.p_set = []
		self.figure.set_canvas(self.canvas)
		self.axes_normal.clear()
		self.axes_1diff.clear()
		self.axes_2diff.clear()
		self.canvas.draw()

	def setup(self):
                """����y���ǩ��x���ǩ"""
		self.axes_normal.set_xlabel("Fetch date")
		self.axes_normal.set_ylim(0)

		self.axes_normal.set_yticks(range(0,1500,100))
		self.axes_normal.set_title('General')

		self.axes_1diff.set_title('1-diff')

		self.axes_2diff.set_title('2-diff')

	def legend(self):
		legends = []
		if len(self.clb_style.GetChecked()) == 0:
		    return
		if self.clb_type.IsChecked(0):
			legend = self.axes_normal.legend(loc=2)
			legends.append(legend)
		if self.clb_type.IsChecked(1):
			legend = self.axes_1diff.legend(loc=2)
			legends.append(legend)
		if self.clb_type.IsChecked(2):
			legend = self.axes_2diff.legend(loc=2)
			legends.append(legend)
		for legend in legends:
			for label in legend.get_lines():
				label.set_linewidth(2)
		self.canvas.draw()

	def unlegend(self):

		if self.clb_type.IsChecked(0):
		    self.axes_normal.legend().set_visible(False)
		if self.clb_type.IsChecked(1):
		    self.axes_1diff.legend().set_visible(False)
		if self.clb_type.IsChecked(2):
		    self.axes_2diff.legend().set_visible(False)
		self.canvas.draw()



class myframe(wx.Frame):

	def __init__(self):

		wx.Frame.__init__(self, None, -1, "�ɻ�Ʊ�۸��ͼ", style= wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
| wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
		self.Maximize()
		# ���ݳ�Ա
		self.fl_lines = {}

		# ����һ���ָ
		self.sp = wx.SplitterWindow(self)
		# ���������
		self.myquery = myquery(self.sp)
		self.myplot = myplot(self.sp)
		# self.p1.SetBackgroundColour("pink")
		# self.p2.SetBackgroundColour("sky blue")
		# ȷ�����õ�����屻����
		# self.p1.Hide()
		# self.p2.Hide()
		# ��ʼ���ָ����
		self.sp.SplitVertically(self.myquery, self.myplot,500)


		# ���ò˵���
		menubar = wx.MenuBar()
		# �����˵�
		menu = wx.Menu()
		menubar.Append(menu, "����")
		ftfile = menu.Append(-1, "����", "ѡ����Ҫ�򿪵ĺ����ļ�")
		menu.AppendSeparator()
		pcfile = menu.Append(-1, "�۸�", "ѡ����Ҫ�򿪵ļ۸��ļ�")

		menu = wx.Menu()
		menubar.Append(menu, "ģ��")
		decision_tree = menu.Append(-1, "������", "ʹ�þ������������н�ģ")

		self.Bind(wx.EVT_MENU, self.OnOpenFile, ftfile)
		self.Bind(wx.EVT_MENU, self.OnOpenFile, pcfile)
		self.Bind(wx.EVT_MENU, self.decision_tree1, decision_tree)
		self.SetMenuBar(menubar)

	def OnOpenFile(self, evt):

		wildcard = "txt source (*.txt)|*.txt"
		dialog = wx.FileDialog(self, "Choose a file", os.getcwd(),
		                       "", wildcard, wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			path = dialog.GetPath()
			#�õ��˵���
			item = self.GetMenuBar().FindItemById(evt.GetId())
			text = item.GetText()
			if text == "����".decode('gbk'):
				self.init_flightlines(path)
			elif text == "�۸�".decode('gbk'):
				self.init_pricelist(path)

		dialog.Destroy()

	def decision_tree1(self, evt):
		import treepredict
		reload(treepredict)
		full_price = 1130
		flights = self.fl_lines[('PEK','PVG')].set_of_flights

		data = []
		for deptid in flights.keys():
			flight = flights[deptid]
			ftype = flight['ftype']
			deptdate = flight['date']
			deptdate = deptdate.split('/')

			# ����ܼ�
			weekday = datetime.datetime(int(deptdate[0]),int(deptdate[1]),int(deptdate[2])).weekday()
			weekday = int(weekday)
			#print weekday
			time = flight['time']

			# �����ʱ��ǳ�����߷ǳ���ȡΪ1������Ϊ0
			if int(time[0:2]) < 9 or int(time[0:2]) > 20:
				time = 1
			else:
				time = 0

			# ����۸�
			dd = flight['date']

			# str-->date
			dd = dd.split('/')
			deptdate = datetime.date(int(dd[0]), int(dd[1]), int(dd[2]))
			price = flight['price']

			points = []
			for ftdate in price.keys():
				ff = ftdate.split('/')
				fetchdate = datetime.date(int(ff[0]), int(ff[1]), int(ff[2]))
				days = (deptdate-fetchdate).days
				points.append((days, price[ftdate]))

			points = self.pre(points)
			p = []
			for i in points.keys():
				if i >= 6:
					p.append(points[i])

			#print p
			if len(p) <= 1:
				continue
			result_price = p[0]
			p.pop(0)
			avg_price = sum(p)/len(p)

			result_price = int(float(result_price)/float(full_price)*10)
			avg_price = int(float(avg_price)/float(full_price)*10)

			data.append((weekday, time, avg_price, result_price))
##		fout = open('task.txt', 'w')
##		lines = ['%s %s %s %s\n' %v for v in data]
##		fout.writelines(lines)
##		fout.close()
		flighttree = treepredict.buildtree(data, scoref = treepredict.giniimpurity)
		treepredict.drawtree(flighttree,'flighttree_entropy.jpg')


	def pre(self, points):
		points = sorted(points,key = lambda x:x[0])
		x = []
		y = []

		for p in points:
		    x.append(p[0])
		    y.append(p[1])

		#print points
		try:
		    y_max = max(y)
		except:
		    pass
		for i in range(points[-1][0]):
		    if i not in x:
		        x.insert(i,i)
		        if i == 0:
		            y.insert(0,y_max)
		        else:
		            y.insert(i,y[i-1])
		        #print x
		        #print y


		points = {}
		for i in range(len(x)):
		    points[x[i]] = y[i]

		return points

	def init_flightlines(self, filepath):
		fin = open(filepath, 'r')
		lines = fin.readlines()
		n = 0
		for line in lines:
			line.strip()
			s = line.split(',')
			dp_arr = (s[1], s[2])

			# �������ڸú��ߣ��������������
			if dp_arr not in self.fl_lines.keys():
				self.fl_lines[dp_arr] = flightline(s[1], s[2])

			aline = self.fl_lines[dp_arr]
			#��Ӹú��ߵĺ��� deptid, flightid, date, time, type
			if not aline.is_in_set(s[6][:-1]):
				aline.add_new(s[6][:-1], s[0], s[4], s[5], s[3])
				n += 1
		fin.close()

		self.myquery.add_city(self.fl_lines.keys())

		wx.MessageBox("You added %s flights." % n)

	def init_pricelist(self, filepath):
		fin = open(filepath, 'r')
		lines = fin.readlines()

		# ÿһ����deptdate,fetchdate,price
		for line in lines:
			line.strip()
			s = line.split(',')
			myline = None
			for dp_arr in self.fl_lines.keys():
				if self.fl_lines[dp_arr].is_in_set(s[0]):
					myline = self.fl_lines[dp_arr]
					break
			if myline == None:
				wx.MessageBox("No such a flight in the app with deptID %s, the process is stopped." % s[0])
				return
			myline.add_price(s[0], s[1], s[2])
		fin.close()
		wx.MessageBox("You added %s prices." % str(len(lines)))



if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = myframe()
	frame.Show()
##	root, dirs, files = os.walk(r'.\data')
##	filepaths = []

	frame.init_flightlines("flight.txt")
	frame.init_pricelist("price.txt")
	#print frame.fl_lines[('PEK','PVG')].get_flights_by_dpdate('2014/08/12')

	frame.myquery.ch_arrcity.SetSelection(0)
	frame.myquery.ch_dpcity.SetSelection(0)
	frame.myplot.clb_style.Check(0)
	frame.myplot.clb_type.Check(0)
	app.MainLoop()
