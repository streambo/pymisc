# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import balLogger as logb
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool
import matplotlib.pyplot as plt

from strader import Trader

prices = ps = phs = pls = None

rsis = None

def runStrategy(in_prices):
	global prices, ps, phs, pls, rsis
	
	log.debug('beginning s5 strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	phs = [p['high'] for p in prices]
	pls = [p['low'] for p in prices]
	rsis = rsi.calc_rsi(prices, 14)
	
	pool = StrategyPool(50)
	doTrade(pool, 1, 180, 12, 0.5, -0.6)
	pool.showStrategies()
	return
	
	direction = 1
	starttime = time.time() 
	for i in range(30, 150)[::10]:
		for j in range(2, 30)[::5]:
			if i < j: continue
			elapsed = long(time.time() - starttime)
			log.debug('== ' + str(elapsed) + ', ' + str(i) + ',' + str(j) + ' ==')
			for kp in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]:
				for kl in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]:
					doTrade(pool, direction, i, j, kp, -kl)
	
	pool.showStrategies()
	
	return
	
def doTrade(pool, direction, lPeriod, sPeriod, profitLevel, lossLevel):
	global prices, ps, phs, pls, rsis
	
	sname = 'S5_' + str(direction) + '_' + str(lPeriod) + '_' + str(sPeriod) + '_' + str(profitLevel) + '_' + str(-lossLevel)
	
	t = Trader(sname)
	front = lPeriod + sPeriod - 1
	lastPrice = 0
	for i in range(front, len(prices)):
		price = prices[i]
		volume, notes = 0, ''
		
		slope = midy = None
		highSlope = highy = lowSlope = lowy = None
		nSlope = ny = None
		
		#cSlope = cy = None
		if t.position > 0 and price['rmb'] < prices[i-1]['rmb']:
			profit = (price['rmb'] - lastPrice) * 100 / lastPrice
			
			if profit >= profitLevel:
				notes = 'PROFIT'
				volume = 0 - t.position
			elif profit <= lossLevel:
				notes = 'LOSS'
				volume = 0 - t.position
				
		elif t.position < 0 and price['rmb'] > prices[i-1]['rmb']:
			profit = (lastPrice - price['rmb']) * 100 / lastPrice
			
			if profit >= profitLevel:
				notes = 'PROFIT'
				volume = 0 - t.position
			elif profit <= lossLevel:
				notes = 'LOSS'
				volume = 0 - t.position
				
		elif t.position == 0:
			nSlope, ny = calc_slope(ps[i - sPeriod + 1 : i + 1])
			
			if (direction == 1 and nSlope > 0) or (direction == -1 and nSlope < 0):
				ys = ps[i - lPeriod - sPeriod + 2 : i - sPeriod + 2]
				slope, midy = calc_slope(ys)
				#print i - lPeriod - sPeriod + 2,  i - sPeriod + 2
				highSlope, highy, lowSlope, lowy = calc_bands(ys)
				
				#print i - lPeriod - sPeriod + 2,  i - sPeriod + 2
				x = lPeriod + sPeriod - 2
				p = ps[i]
				high, low, mid = highy(x), lowy(x), midy(x)
				
				if direction == 1 and p > high and nSlope > 0 and high > mid and mid > low and t.position <= 0:
					notes = 'BUY'
					volume = 1
				elif direction == -1 and p < low and nSlope < 0 and high > mid and mid > low and t.position >= 0:
					notes = 'SELL'
					volume = -1
			
		if volume != 0:
			lastPrice = price['rmb']
			t.processOrder(price['dt'], price['rmb'], volume, notes=notes)
		else:
			t.summary(price['dt'], price['rmb'])
		
		#logb.info(str(i) + ',' + str(price['dt']) + ',' + str(std) + ',' + str(notes) + ',' + str(volume)
		#			+ ',' + str(p) + ',' + str(low) + ',' + str(mid) + ',' + str(high) + ',' + str(price['rmb'])
		#			+ ',' + str(slope) + ',' + str(nSlope)+ ',' + str(highSlope) + ',' + str(lowSlope))
		
		if volume != 0 and i >= 1:
			print i, rsis['rsi'][i]
		
			nxs = nys = []
			if ny:
				nxs = range(sPeriod)
				nys = map(ny, nxs)
				nxs = map(lambda x: x + lPeriod - 1, nxs)
			
			xs = upys = lowys = midys = []
			if highy:
				xs = range(lPeriod)
				upys = map(highy, xs)
				lowys = map(lowy, xs)
				midys = map(midy, xs)
			
			#cxs = cys = []
			#if cy:
			#	cxs = range(cPeriod)
			#	cys = map(cy, cxs)
			#	cxs = map(lambda x: x + lPeriod - 1, cxs)
			
			axs = range(lPeriod + sPeriod + 100)
			ays = ps[i - lPeriod - sPeriod + 2 : i + 102]
			if lPeriod + sPeriod + 100 > len(ps):
				axs = range(len(ps) - lPeriod - sPeriod + 2)
				ays = ps[i - lPeriod - sPeriod + 2 : ]
			plt.plot(axs, ays, 'b', xs, midys, 'y', xs, upys, 'r', xs, lowys, 'g', nxs, nys, 'm')
			plt.vlines(lPeriod + sPeriod - 2, min(ays), max(ays), color='y', linestyles ='dotted')
			plt.title(str(price['dt']) + ' ' + str(volume) + ' ' + str(notes))
			plt.show()
			
	
	pool.estimate(t)
	return t

def calc_slope(datas):
	#print datas
	l = len(datas)
	xs = np.arange(l)
	xsT = np.array([xs, np.ones(l)]).T
	m, c = np.linalg.lstsq(xsT, datas)[0]
	midy = lambda x: m * x + c
	return round(m, 3), midy
	
def calc_bands(ys):
	l = len(ys)
	high1 = int(l/2)
	low1 = int(l/2)
	high2 = ys.index(max(ys))
	low2 = ys.index(min(ys))
	#high1 = high2 = low1 = low2 = 0
	highsm = lowsm = float('inf')
	
	for x in range(0, l):
		if high1 != x:
			ty, sm, slope = genLine(high1, x, ys, 1)
			if sm < highsm:
				high2 = x
				highsm, highy, highSlope = sm, ty, slope
		
		if high2 != x and high1 != high2:
			ty, sm, slope = genLine(high2, x, ys, 1)
			if sm < highsm:
				high1, high2 = high2, x
				highsm, highy, highSlope = sm, ty, slope
		
		if low1 != x:
			ty, sm, slope = genLine(low1, x, ys, -1)
			if sm < lowsm:
				low2 = x
				lowsm, lowy, lowSlope = sm, ty, slope
		
		if low2 != x:# and low1 != low2:
			ty, sm, slope = genLine(low2, x, ys, -1)
			if sm < lowsm:
				low1, low2 = low2, x
				lowsm, lowy, lowSlope = sm, ty, slope
	
	return highSlope, highy, lowSlope, lowy
	
def genLine(x1, x2, ys, tp):
	#print x1, x2
	slope = (ys[x1] - ys[x2]) / (x1 - x2)
	c = ys[x1] - slope * x1
	
	y = lambda x: slope * x + c
	
	l = len(ys)
	sm = 0
	for i in range(l):
		
		if tp == 1 and ys[i] > y(i) + 0.003:
			return y, float('inf'), slope
		elif tp == -1 and ys[i] < y(i) - 0.001:
			return y, float('inf'), slope
		sm += y(i) - ys[i]
		
	sm = sm * tp
	#print x1, x2, sm
	return y, sm, slope
	
