# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool

def runStrategy(prices):
	log.debug('beginning l4 strategy ...')
	
	ps = [p['close'] for p in prices]
	
	pool = StrategyPool(50)
	#doTrade(pool, prices, ps, 3, 9)
	#pool.showStrategies()
	#return
	
	for i in range(5, 40)[::2]:
		for j in range(3, 30)[::2]:
			doTrade(pool, prices, ps, i, j)
				
	pool.showStrategies()

def doTrade(pool, prices, ps, near, far):
	
	sname = 'L2_' + str(near) + '_' + str(far)
	phighs = [p['high'] for p in prices]
	plows = [p['low'] for p in prices]
	
	front = max(near, far)
	
	t = Trader(sname)
	direct = odirect = 0
	for i in range(front, len(prices)):
		price = prices[i]
		
		
		span = 3
		if phighs[i] > phighs[i - 1] and plows[i] > plows[i - 1]:
			nearLow, nearLowIndex = findLow(phighs, plows, i - span + 1, i)
			nearHigh, nearHighIndex = findHigh(phighs, plows, nearLowIndex - span + 1, nearLowIndex)
			farLow, farLowIndex = findLow(phighs, plows, nearHighIndex - span + 1, nearHighIndex)
			farHigh, farHighIndex = findHigh(phighs, plows, farLowIndex - span + 1, farLowIndex)
			
		elif phighs[i] < phighs[i - 1] and plows[i] > plows[i - 1]:
			nearHigh, nearHighIndex = findHigh(phighs, plows, i - span + 1, i)
			nearLow, nearLowIndex = findLow(phighs, plows, nearHighIndex - span + 1, nearHighIndex)
			farHigh, farHighIndex = findHigh(phighs, plows, nearLowIndex - span + 1, nearLowIndex)
			farLow, farLowIndex = findLow(phighs, plows, farHighIndex - span + 1, farHighIndex)
			
		else:
			continue
			
			
		for j in range(i - span + 1, i + 1):
			if phighs[j] > nearHigh: nearHigh, nearHignIndex = phighs[j], j
			if plows[j] < nearLow: nearLow, nearLowIndex = plows[j], j
		if nearHignIndex = i
		
def findLow(phighs, plows, start, end):
	lowest = min(plows[start : end+1])
	if plows[start] == lowest: return findLow(phighs, plows, start-1, end)
	return lowest
	
	low = 9999999
	for i in range(start, pos + 1):
		if plows[i] < low: low, lowIndex = plows[i], i
		
	if 
		
		
def findHighAndLow(phighs, plows, start, pos):
	for j in range(start, pos + 1):
		if phighs[j] > high: high, hignIndex = phighs[j], j
		if plows[j] < low: low, lowIndex = plows[j], j
	
	if hignIndex != start and hignIndex != pos:
		high found
	elif hignIndex == pos:
		findHighAndLow(phighs, plows, lowindex - 1, lowindex)
	elif hignIndex == start:
		findHighAndLow(phighs, plows, start - 1, pos)
		
	if nearLowIndex != start and nearLowIndex != pos:
		low found
	
	if nearHignIndex == pos and nearLowIndex == start:
		findHighAndLow(phighs, plows, span + 1, pos)
	elif nearHignIndex == pos
		
	
		
		
		
		nearHigh = -9999999
		nearLow = 9999999
		nearHignIndex = nearLowIndex = 0
		for j in range(i - near + 1, i + 1):
			if phighs[j] > nearHigh: nearHigh, nearHignIndex = phighs[j], j
			if plows[j] < nearLow: nearLow, nearLowIndex = plows[j], j
		
		farHigh = -9999999
		farLow = 9999999
		farHignIndex = farLowIndex = 0
		for j in range(i - far + 1, i + 1):
			if phighs[j] > farHigh: farHigh, farHignIndex = phighs[j], j
			if plows[j] < farLow: farLow, farLowIndex = plows[j], j
		
		highGauge = lowGauge = 0
		if nearHignIndex != farHignIndex:
			highGauge = nearHigh - (farHigh - nearHigh) * (i - nearHignIndex) / (farHignIndex - nearHignIndex)
			if plows[i] > highGauge:
				direct 
			
		if nearHignIndex == farHignIndex:
			lowGauge = nearLow - (farLow - nearLow) * (i - nearLowIndex) / (farLowIndex - nearLowIndex) 
			
		if 
		
		
		
		for j in range(i - slowing + 1, i + 1):
		nearHigh = max(phighs[i-near+1 : i+1])
		nearLow = min(plows[i-near+1 : i+1])
		farHigh = max(phighs[i-far+1 : i+1])
		farLow = min(plows[i-far+1 : i+1])
		
		if 
		
		
	
	pdiff = map(lambda f,s: f - s, phighs, plows)
	
	t = Trader(sname)
	direct = odirect = 0
	for i in range(front, len(prices)):
		price = prices[i]
		
		diffavg = np.mean(pdiff[i-ssp : i+1])
		highest = max(phighs[i-ssp+1 : i+1])
		lowest = min(plows[i-ssp+1 : i+1])
		
		smin = lowest + (highest - lowest) * risk / 100
		smax = highest - (highest - lowest) * risk / 100
		
		if ps[i] < smin:
			direct = -1
		elif ps[i] > smax:
			direct = 1
			
		volume = 0
		if odirect == -1 and direct == 1:
			volume = 1
		elif odirect == 1 and direct == -1:
			volume = -1
			
		odirect = direct
		t.processOrder(price['dt'], price['rmb'], volume * 1000, cntNo=0, notes='')
		
	pool.estimate(t)
	return
	
