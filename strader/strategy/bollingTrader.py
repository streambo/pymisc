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
	
	#doBollingTrade(pool, prices, ps, 12, 2.4)
	#pool.showStrategies()
	#return
	
	for i in range(2, 40):
		j = 0
		log.debug(i)
		while j <= 5:
			doBollingTrade(pool, prices, ps, i, j)
			j += 0.1
	
	pool.showStrategies()
	
def doBollingTrade(pool, prices, ps, period, deviate):
	global highest
	
	sname = 'BOLLING_' + str(period) + '_' + str(deviate)
	bollings = bolling.calc_bolling(prices, period, deviate)
	t = Trader(sname)
	
	for i in range(period, len(prices)):
		if ps[i-1] > bollings['lower'][i-1] and ps[i] < bollings['lower'][i] and t.bsflag < 1:
			notes = 'LAST p: ' + str(ps[i - 1]) + ';boll lower: ' + str(bollings['lower'][i-1]) + 'CURRENT p: ' + str(ps[i]) + ';boll lower: ' + str(bollings['lower'][i])
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if ps[i-1] < bollings['mean'][i-1] and ps[i] >= bollings['mean'][i] and t.bsflag == 1:
			notes = 'LAST p: ' + str(ps[i - 1]) + ';boll mean: ' + str(bollings['mean'][i-1]) + 'CURRENT p: ' + str(ps[i]) + ';boll mean: ' + str(bollings['mean'][i])
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if ps[i-1] < bollings['upper'][i-1] and ps[i] > bollings['upper'][i] and t.bsflag > -1:
			notes = 'LAST p: ' + str(ps[i - 1]) + ';boll upper: ' + str(bollings['upper'][i-1]) + 'CURRENT p: ' + str(ps[i]) + ';boll upper: ' + str(bollings['upper'][i])
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if ps[i-1] > bollings['mean'][i-1] and ps[i] <= bollings['mean'][i] and t.bsflag == -1:
			notes = 'LAST p: ' + str(ps[i - 1]) + ';boll mean: ' + str(bollings['mean'][i-1]) + 'CURRENT p: ' + str(ps[i]) + ';boll mean: ' + str(bollings['mean'][i])
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		t.show(prices[i]['date'], prices[i]['time'], prices[i]['rmb'])
	
	pool.estimate(t)
	
	