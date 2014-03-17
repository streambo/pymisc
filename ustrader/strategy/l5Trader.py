# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
import matplotlib.pyplot as plt
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool

#tolerate = 5

def runStrategy(prices):
	log.debug('beginning l5 strategy ...')
	
	ps = [p['close'] for p in prices]
	
	ys = ps[556:656]
	l = len(ys)
	slope, midy = calc_slope(ys)
	xs = range(l)
	midys = map(midy, xs)
	std = np.std(ys, dtype=np.float64, ddof=0)
	upys = map(lambda y: y + std * 1.2, midys)
	lowys = map(lambda y: y - std * 1.2, midys)
	
	plt.plot(xs, ys, 'b', xs, midys, 'y', xs, upys, 'r', xs, lowys, 'g')#, nxs, nys, 'm')
	
	#plt.plot(xs, ys, 'b-', xs, upys, 'r-', xs, lowys, 'g-')
	plt.show()
	return
	
	
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
		
		if high2 != x:
			ty, sm, slope = genLine(high2, x, ys, 1)
			if sm < highsm:
				high1, high2 = high2, x
				highsm, highy, highSlope = sm, ty, slope
		
		if low1 != x:
			ty, sm, slope = genLine(low1, x, ys, -1)
			#print low1, x, sm, lowsm
			if sm < lowsm:
				low2 = x
				lowsm, lowy, lowSlope = sm, ty, slope
				#print low1, low2, sm
		
		if low2 != x: # and low1 != low2:
			ty, sm, slope = genLine(low2, x, ys, -1)
			#print low2, x, sm, lowsm
			if sm < lowsm:
				low1, low2 = low2, x
				lowsm, lowy, lowSlope = sm, ty, slope
	
	#return highy, lowy
	#print highSlope, lowSlope
	xs = range(l)
	upys = map(highy, xs)
	lowys = map(lowy, xs)
	
	plt.plot(xs, ys, 'b-', xs, upys, 'r-', xs, lowys, 'g-')
	plt.show()
	return
	

def calc_slope(datas):
	#print datas
	l = len(datas)
	xs = np.arange(l)
	xsT = np.array([xs, np.ones(l)]).T
	m, c = np.linalg.lstsq(xsT, datas)[0]
	midy = lambda x: m * x + c
	return round(m, 3), midy
	
def genLine(x1, x2, ys, tp):
	#print x1, x2
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
	
	if tp == -1: print x1, x2, sm
	return y, sm, slope
	
	
	
	
	