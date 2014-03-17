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

def runStrategy(in_prices):
	global prices, ps, phs, pls
	log.debug('beginning s4 strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	phs = [p['high'] for p in prices]
	pls = [p['low'] for p in prices]
	
	pool = StrategyPool(100)
	doTrade(pool, 110, 17, 17)
	pool.showStrategies()
	return
	
	starttime = time.time() 
	for i in range(10, 250)[::10]:
		for j in range(2, 50)[::5]:
			if i < j: continue
			elapsed = long(time.time() - starttime)
			log.debug('== ' + str(elapsed) + ', ' + str(i) + ',' + str(j) + ' ==')
			for k in range (2, 50)[::5]:
				if i < k: continue
				doTrade(pool, i, j, k)
	
	pool.showStrategies()
	
	return
	
def doTrade(pool, lPeriod, sPeriod, cPeriod):
	global prices, ps, phs, pls
	
	sname = 'S4_' + str(lPeriod) + '_' + str(sPeriod) + '_' + str(cPeriod)
	
	t = Trader(sname)
	front = lPeriod + max(sPeriod, cPeriod) - 1
	lastbuy = lastsell = 0
	for i in range(front, len(prices)):
		price = prices[i]
		
		ys = ps[i - lPeriod - sPeriod + 2 : i - sPeriod + 2]
		slope, midy = calc_slope(ys)
		highSlope, highy, lowSlope, lowy = calc_bands(ys)
		nSlope, ny = calc_slope(ps[i - sPeriod + 1 : i + 1])
		
		#std = round(np.std(ys, dtype=np.float64, ddof=0), 3)
		#if i == 122: print i - lPeriod - sPeriod + 1, i - sPeriod + 1, highSlope, lowSlope
		
		x = lPeriod + sPeriod - 2
		p = ps[i]
		volume = 0
		notes = ''
		high, low, mid = highy(x), lowy(x), midy(x)
		
		if p > high and nSlope > 0 and high > mid and mid > low and t.position <= 0:
			notes = 'BUY'
			volume = 0
		elif p < low and nSlope < 0 and high > mid and mid > low and t.position >= 0:
			notes = 'SELL'
			volume = -1
			
		cSlope = cy = None
		if t.position > 0:
			cSlope, cy = calc_slope(ps[i - cPeriod + 1 : i + 1])
			if cSlope < 0:
				notes += '&CLOSE'
				volume -= t.position
		elif t.position < 0:
			cSlope, cy = calc_slope(ps[i - cPeriod + 1 : i + 1])
			if cSlope > 0:
				notes += '&CLOSE'
				volume -= t.position
		
		#logb.info(str(i) + ',' + str(price['dt']) + ',' + str(std) + ',' + str(notes) + ',' + str(volume)
		#			+ ',' + str(p) + ',' + str(low) + ',' + str(mid) + ',' + str(high) + ',' + str(price['rmb'])
		#			+ ',' + str(slope) + ',' + str(nSlope)+ ',' + str(highSlope) + ',' + str(lowSlope))
		
		if volume != 0 and i >= 100000000:
			xs = range(lPeriod)
			upys = map(highy, xs)
			lowys = map(lowy, xs)
			midys = map(midy, xs)
			nxs = range(sPeriod)
			nys = map(ny, nxs)
			nxs = map(lambda x: x + lPeriod - 1, nxs)
			
			cxs = cys = []
			if cy:
				cxs = range(cPeriod)
				cys = map(cy, cxs)
				cxs = map(lambda x: x + lPeriod - 1, cxs)
			
			axs = range(lPeriod + sPeriod + 100)
			ays = ps[i - lPeriod - sPeriod + 2 :i + 102]
			plt.plot(axs, ays, 'b', xs, midys, 'y', xs, upys, 'r', xs, lowys, 'g', nxs, nys, 'm', cxs, cys, 'k')
			plt.title(str(price['dt']) + ' ' + str(volume))
			plt.show()
			
		t.processOrder(price['dt'], price['rmb'], volume, notes=notes)
	
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
	high1 = high2 = low1 = low2 = 0
	highsm = lowsm = float('inf')
	
	for x in range(1, l):
		ty, sm, slope = genLine(high1, x, ys, 1)
		if sm < highsm:
			high2 = x
			highsm, highy, highSlope = sm, ty, slope
		
		if high2 != x and high1 != high2:
			ty, sm, slope = genLine(high2, x, ys, 1)
			if sm < highsm:
				high1, high2 = high2, x
				highsm, highy, highSlope = sm, ty, slope
		
		ty, sm, slope = genLine(low1, x, ys, -1)
		if sm < lowsm:
			low2 = x
			lowsm, lowy, lowSlope = sm, ty, slope
		
		if low2 != x and low1 != low2:
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
		
		if tp == 1 and ys[i] > y(i) + 0.001:
			return y, float('inf'), slope
		elif tp == -1 and ys[i] < y(i) - 0.001:
			return y, float('inf'), slope
		sm += y(i) - ys[i]
		
	sm = sm * tp
	#print x1, x2, sm
	return y, sm, slope
	
