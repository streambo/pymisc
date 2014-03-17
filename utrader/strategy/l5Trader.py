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
	
	ys = ps[55:110]
	l = len(ys)
	high1 = high2 = low1 = low2 = 0
	highsm = lowsm = float('inf')
	for x in range(1, l):
		ty, sm = genLine(high1, x, ys, 1)
		if sm < highsm:
			high2 = x
			highsm, highy = sm, ty
		
		if high2 != x and high1 != high2:
			ty, sm = genLine(high2, x, ys, 1)
			if sm < highsm:
				high1, high2 = high2, x
				highsm, highy = sm, ty
		
		ty, sm = genLine(low1, x, ys, -1)
		if sm < lowsm:
			low2 = x
			lowsm, lowy = sm, ty
		
		if low2 != x and low1 != low2:
			ty, sm = genLine(low2, x, ys, -1)
			if sm < lowsm:
				low1, low2 = low2, x
				lowsm, lowy = sm, ty
	
	#return highy, lowy
	
	xs = range(l)
	upys = map(highy, xs)
	lowys = map(lowy, xs)
	
	plt.plot(xs, ys, '-', xs, upys, '-', xs[:50], lowys[:50], '-')
	plt.show()
	return
	
	
def genLine(x1, x2, ys, tp):
	#print x1, x2
	slope = (ys[x1] - ys[x2]) / (x1 - x2)
	c = ys[x1] - slope * x1
	
	y = lambda x: slope * x + c
	
	l = len(ys)
	tolerate = l / 20
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
	return y, sm
	
	
	
	
	