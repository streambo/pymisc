# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import balLogger as logb
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool

import matplotlib.pyplot as plt

def runStrategy(in_prices):
	log.debug('beginning s3 strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
	pool = StrategyPool(50)
	doTrade(pool, prices, ps, 90, 17, 45)
	pool.showStrategies()
	return
	
	for i in range(10, 100)[::10]:
		for j in range(2, 30)[::5]:
			log.debug('== ' + str(i) + ' , ' + str(j) + ' ==')
			for k in range (5, 100)[::20]:
				doTrade(pool, prices, ps, i, j, k)
	
	pool.showStrategies()
	
	return
	
def doTrade(pool, prices, ps, lPeriod, sPeriod, plusSpan):
	
	sname = 'S3_' + str(lPeriod) + '_' + str(sPeriod) + '_' + str(plusSpan)
	
	t = Trader(sname)
	front = lPeriod + sPeriod - 1
	lastbuy = lastsell = 0
	for i in range(front, len(prices)):
		price = prices[i]
		
		ys = ps[i - lPeriod - sPeriod + 2 : i - sPeriod + 2]
		slope, midy = calc_slope(ys)
		highSlope, highy, lowSlope, lowy = calc_bands(ys)
		nSlope, ny = calc_slope(ps[i - sPeriod + 1 : i + 1])
		
		std = round(np.std(ys, dtype=np.float64, ddof=0), 3)
		#if i == 122: print i - lPeriod - sPeriod + 1, i - sPeriod + 1, highSlope, lowSlope
		
		x = lPeriod + sPeriod - 2
		p = ps[i]
		volume = 0
		notes = ''
		cntNo = 0
		closing = False
		high, low, mid = highy(x), lowy(x), midy(x)
		
		#if slope < 0 and nSlope < 0 and p < high and p > mid and high - p > p - mid and high > mid and mid > low:
		#	notes = '1'
		#	volume = -1
		#elif slope > 0 and nSlope > 0 and p > low and p < mid and p - low > mid - p and high > mid and mid > low:
		#	notes = '2'
		#	volume = 1
		if p > high and nSlope > 0 and high > mid and mid > low:
			notes = '3'
			volume = 1
		elif p < low and nSlope < 0 and high > mid and mid > low:
			notes = '4'
			volume = -1
			
		
		if volume == 1 and ((t.counters[0].position > 0 and i - lastbuy < plusSpan) or t.counters[0].position > 3): volume = 0
		if volume == -1  and ((t.counters[0].position < 0 and i - lastsell < plusSpan) or t.counters[0].position < -3): volume = 0
		if volume == 1: lastbuy = i
		if volume == -1: lastsell = i
		
		if nSlope < 0 and t.counters[0].position > 0 and volume == 0:
			volume, closing = -1, True
			
		if nSlope > 0 and t.counters[0].position < 0 and volume == 0:
			volume, closing = 1, True
		
		#logb.info(str(i) + ',' + str(price['dt']) + ',' + str(std) + ',' + str(notes) + ',' + str(volume)
		#			+ ',' + str(p) + ',' + str(low) + ',' + str(mid) + ',' + str(high) + ',' + str(price['rmb'])
		#			+ ',' + str(slope) + ',' + str(nSlope)+ ',' + str(highSlope) + ',' + str(lowSlope))
		
		if volume != 0 and i >= 100000:
			xs = range(lPeriod)
			upys = map(highy, xs)
			lowys = map(lowy, xs)
			midys = map(midy, xs)
			nxs = range(sPeriod)
			nys = map(ny, nxs)
			nxs = map(lambda x: x + lPeriod - 1, nxs)
			
			axs = range(lPeriod + sPeriod + 100)
			ays = ps[i - lPeriod - sPeriod + 2 :i + 102]
			plt.plot(axs, ays, 'b-', xs, midys, 'y-', xs, upys, 'r-', xs, lowys, 'g-', nxs, nys, 'c-')
			plt.title(str(price['dt']) + ' ' + str(volume) + ' ' + str(closing))
			plt.show()
			
		t.processOrder(price['dt'], price['rmb'], volume, cntNo=cntNo, notes=notes, closing=closing)
	
	pool.estimate(t)
	return t

def calc_slope(datas):
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
	tolerate = 0
	breaks = sm = 0
	for i in range(l):
		if tp == 1 and ys[i] > y(i) + 0.001:
			breaks += 1
		elif tp == -1 and ys[i] < y(i) - 0.001:
			breaks += 1
		sm += y(i) - ys[i]
		
	sm = sm * tp
	if breaks > tolerate:
		sm = float('inf')
	
	#print x1, x2, sm
	return y, sm, slope
	
