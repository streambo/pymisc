# -*- coding: utf-8 -*-
import datetime, time, csv, os
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool

highest = 0

def runStrategy(prices):
	logs.info('STRATEGY,BUY TIMES, SELL TIMES, FINAL EQUITY')
	
	#prices = SqliteDB().getAllPrices(table)
	ps = [p['close'] for p in prices]
	pool = StrategyPool(100)
	
	doKDJTrade(pool, prices, 5, 3, 3)
	pool.showStrategies()
	return
	
	for i in range(3, 30):
		for j in range(70, 100):
			for k in range(1, 31):
				doKDJTrade(pool, prices, i, j, k)
	
	pool.showStrategies()
	
def doKDJTrade(pool, prices, kPeriod, dPeriod, slowing):
	global highest
	
	sname = 'KDJ_' + str(kPeriod) + '_' + str(dPeriod) + '_' + str(slowing)
	kds = kdj.calc_kd(prices, kPeriod, dPeriod, slowing)
	t = Trader(sname)
	
	for i in range(kPeriod + slowing, len(prices)):
		if kds['k'][i-1] <= 30 and kds['k'][i-1] < kds['d'][i-1] and kds['k'][i] > kds['d'][i]:
			notes = 'KDJ: pre' + str(kds['k'][i-1]) + ';' + str(kds['d'][i-1]) + ';cur: ' + str(kds['k'][i]) + ';' + str(kds['d'][i])
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
	
		if kds['k'][i-1] >= 70 and kds['k'][i-1] > kds['d'][i-1] and kds['k'][i] < kds['d'][i]:
			notes = 'KDJ: pre' + str(kds['k'][i-1]) + ';' + str(kds['d'][i-1]) + ';cur: ' + str(kds['k'][i]) + ';' + str(kds['d'][i])
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
		
		t.show(prices[i]['date'], prices[i]['time'], prices[i]['rmb'])
	
	pool.estimate(t)
	
	