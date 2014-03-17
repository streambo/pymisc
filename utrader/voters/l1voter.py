# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import balLogger as logb
from indicator import ma, macd, bolling, rsi, kdj
import matplotlib.pyplot as plt

period, fee = 3, 0.02

def calc_directs(prices):
	ps = [p['close'] for p in prices]
	
	l = len(prices)
	for i in range(l):
		price = prices[i]
		
		direct = 0
		if i + period < l:
			p = prices[i]['rmb']
			nextp = prices[i + period]['rmb']
			
			if nextp - p > 2 * fee:
				direct = 1
			elif nextp - p < -2 * fee:
				direct = -1
			else:
				direct = 0
		
		prices[i]['direct'] = direct
	
def runVoter(prices):
	calc_directs(prices)
	
	ps = [p['close'] for p in prices]
	
	mas7 = ma.calc_ma(ps, 7)
	smas13 = ma.calc_sma(ps, 13)
	
	l = len(prices)
	ops = [0] * l
	stds = [0] * l
	for i in range(7, l):
		stds[i] = 1
		
		if mas7[i] - smas13[i] > 0:
			ops[i] = 1
		elif mas7[i] - smas13[i] < 0:
			ops[i] = -1
			
	goods = [0, 0]
	bads = [0, 0]
	for i in range(7, l):
		j = 0
		if stds[i] >= 1.0: j = 1
		if ops[i] == prices[i]['direct']:
			goods[j] += 1
		else:
			bads[j] += 1
	
	print goods[0], bads[0]
	print goods[1], bads[1]
	return
	dts = [p['dt'] for p in prices]
	directs = [p['direct'] for p in prices]
	
	fig = plt.figure()
	ax1 = fig.add_subplot(211)
	ax1.plot_date(dts, directs, 'b-')
	ax1.plot_date(dts, ops, 'r-')
	ax1.set_ylim(-2,2)
	
	ax2 = fig.add_subplot(212)
	ax2.plot_date(dts, ps, 'b-')
	
	plt.show()
	
#def doScan()