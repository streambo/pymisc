# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import DateFormatter
from matplotlib.widgets import MultiCursor
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import tradesLogger as logtr
from utils.rwlogging import balLogger as logb

SLOPE_PERIOD, PROFIT_DAYS, FEE = 20, 3, 0.01
SLOPE_GUAGE, STD_GUAGE = 0.1, 0.5
AREA_NUM = 4

class VoterPool():
	def __init__(self, num, prices):
		self.num = num
		self.voters = [0] * AREA_NUM
		for area in range(AREA_NUM):
			self.voters[area] = [['', 0, float('inf'), []]]
		self.prices = prices
		self.directs, self.slopes, self.stds, self.areas = calc_variants(prices)
	
	def estimate(self, vname, ops, front):
		l = len(self.directs)
		front = max(front, SLOPE_PERIOD)
		end = l - PROFIT_DAYS
		
		goods = [0] * AREA_NUM
		bads = [0] * AREA_NUM
		for i in range(front, end):
			area = self.areas[i]
			goods[area] += ops[i] * self.directs[i]
			
			#if ops[i] == self.directs[i]:
			#	goods[area] += 1
			#elif self.directs[i] == 0:
			#	pass
			#else:
			#	bads[area] += 1
				
		for area in range(AREA_NUM):
			#logb.info('------' + str(area) + ', ' + str(AREA_NUM)) 
			vts, good, bad = self.voters[area], goods[area], bads[area]
			#logb.info('--' + str(area) + ',' + vname + ',' + str(good) + ',' + str(bad)) 
			gd = good - bad
			if gd < vts[-1][1] - vts[-1][2]: continue
			l = len(vts)
			for i in range(l):
				vgd = vts[i][1] - vts[i][2]
				if gd > vgd:
					logb.info(str(area) + ',' + vname + ',' + str(good) + ',' + str(bad))
					vts.insert(i, [vname, good, bad, ops])
					if l + 1 > self.num:
						vts.pop(-1)
					break
	
	def showVoters(self):
		logs.info('AREA, VOTER, GOOD, BAD')
		for area in range(AREA_NUM):
			vts = self.voters[area]
			l = len(vts)
			#print l
			for i in range(l):
				logs.info(str(area) + ',' + vts[i][0] + ',' + str(vts[i][1]) + ',' + str(vts[i][2]))
				self.graph(area, i + 1, vts[i])
		
	def graph(self, area, no, vt):
		fname = str(area) + '_' + str(no) + '_' + vt[0]
		
		dts = [p['dt'] for p in self.prices]
		ps = [p['close'] for p in self.prices]
		
		l = len(ps)
		directs = []
		ops = []
		for i in range(l):
			if self.areas[i] == area:
				directs.append(self.directs[i] * 10)
				if vt[3][i] == 0: ops.append(None)
				else: ops.append(vt[3][i])
		xs = range(len(directs))
		fig = plt.figure()
		ax1 = fig.add_subplot(211)
		#ax1.xaxis.set_major_formatter(DateFormatter('%m-%d'))
		#ax1.plot_date(dts, self.areas, 'y-')
		#ax1.plot_date(dts, directs, 'b-')
		#ax1.plot_date(dts, ops, 'r-')
		ax1.plot(xs, directs, 'b-', xs, ops, 'r.')
		ax1.grid()
		ax1.set_ylim(-2, 4)
		#ax1.plot_date(dts, stds, 'r-')
		
		ax2 = fig.add_subplot(212)
		ax2.xaxis.set_major_formatter(DateFormatter('%m-%d'))
		ax2.plot_date(dts, ps, 'b-')
		
		plt.savefig(os.path.join(os.path.dirname(__file__), '../result/' + fname + '.png'), dpi=150)
		plt.close(fig)
		#plt.show()

def calc_variants(prices):
	ps = [p['close'] for p in prices]
	
	l = len(prices)
	directs = [0] * l
	slopes = [0.0] * l
	stds = [0.0] * l
	areas = [0] * l
	for i in range(l):
		price = prices[i]
		
		if i + PROFIT_DAYS < l:
			p = prices[i]['rmb']
			nextp = prices[i + PROFIT_DAYS]['rmb']
			
			directs[i] = nextp - p
			
			#if nextp - p > 2 * FEE:
			#	directs[i] = 1
			#elif nextp - p < -2 * FEE:
			#	directs[i] = -1
			#else:
			#	directs[i] = 0
		
		if i < SLOPE_PERIOD - 1: continue
		slopes[i] = calc_slope(ps[i - SLOPE_PERIOD + 1 : i + 1])
		stds[i] = np.std(ps[i - SLOPE_PERIOD + 1 : i + 1], dtype=np.float64, ddof=0)
		
		if slopes[i] >= SLOPE_GUAGE:
			areas[i] = 3
		elif slopes[i] <= -SLOPE_GUAGE:
			areas[i] = 0
		elif slopes[i] > -SLOPE_GUAGE and slopes[i] < SLOPE_GUAGE and stds[i] >= STD_GUAGE:
			areas[i] = 2
		elif slopes[i] > -SLOPE_GUAGE and slopes[i] < SLOPE_GUAGE and stds[i] < STD_GUAGE:
			areas[i] = 1
		else:
			areas[i] = -1
		
	return directs, slopes, stds, areas

def calc_slope(datas):
	#print datas
	l = len(datas)
	xs = np.arange(l)
	xsT = np.array([xs, np.ones(l)]).T
	m, c = np.linalg.lstsq(xsT, datas)[0]
	return m
