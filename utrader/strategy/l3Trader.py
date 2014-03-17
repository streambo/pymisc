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
	log.debug('beginning l3 strategy ...')
	
	ps = [p['close'] for p in prices]
	
	pool = StrategyPool(50)
	#doTrade(pool, prices, ps, 3, 9)
	#pool.showStrategies()
	#return
	
	for i in range(5, 40)[::2]:
		for j in range(3, 30)[::2]:
			doTrade(pool, prices, ps, i, j)
				
	pool.showStrategies()

def doTrade(pool, prices, ps, risk, ssp):
	
	sname = 'L2_' + str(risk) + '_' + str(ssp)
	
	#k = 33 - risk
	
	phighs = [p['high'] for p in prices]
	plows = [p['low'] for p in prices]
	pdiff = map(lambda f,s: f - s, phighs, plows)
	
	front = max(0, ssp)
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
	
