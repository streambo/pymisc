# -*- coding: utf-8 -*-
import datetime, time, csv, os
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool

def runStrategy(prices):
	log.debug('beginning l2 strategy ...')
	
	ps = [p['close'] for p in prices]
	
	
	pool = StrategyPool(50)
	#doTrade(pool, prices, ps, 14, 21, 14)
	#pool.showStrategies()
	#return
	
	
	for i in range(5, 20)[::2]:
		for j in range(12, 50)[::2]:
			if i >= j: continue
			for k in range(10, 40)[::3]:
				for l in [20, 30, 40, 50, 60, 70]:
					doTrade(pool, prices, ps, i, j, k, l)
				#doMacdTrade(pool, prices, ps, i, j, k)
				
	pool.showStrategies()

def doTrade(pool, prices, ps, fast, slow, rsiPeriod, rsiGuage):
	
	sname = 'L2_' + str(fast) + '_' + str(slow) + '_' + str(rsiPeriod) + '_' + str(rsiGuage)
	macds = macd.calc_macd(prices, fast, slow, 7)
	rsis = rsi.calc_rsi(prices, rsiPeriod)
	
	front = max(fast, slow, rsiPeriod)
	
	t = Trader(sname)
	
	direct = odirect = 0
	for i in range(front, len(prices)):
		#print macds['macd'][i], rsis['rsi'][i], odirect , direct
		price = prices[i]
		
		if macds['macd'][i] > 0 and rsis['rsi'][i] > rsiGuage:
			direct = 1
		elif macds['macd'][i] < 0 and rsis['rsi'][i] < rsiGuage:
			direct = -1
		
		volume = 0
		if odirect == -1 and direct == 1:
			volume = 1
		elif odirect == 1 and direct == -1:
			volume = -1
			
		odirect = direct
		t.processOrder(price['dt'], price['rmb'], volume * 1000, cntNo=0, notes='')
	
	pool.estimate(t)
	return
	
