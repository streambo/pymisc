# -*- coding: utf-8 -*-
import datetime, time, csv, os
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool

highest, openLevel, closeLevel = 0, 0.2, 0.1


def runStrategy(prices):
	logs.info('STRATEGY,BUY TIMES, SELL TIMES, FINAL EQUITY')
	
	ps = [p['close'] for p in prices]
	
	pool = StrategyPool(100)
	
	doMacdTrade(pool, prices, ps, 12, 26, 9)
	
	pool.showStrategies()
	return
	
	
	for i in range(5, 20):
		for j in range(12, 50):
			if i >= j: continue
			for k in range(2, 20):
				doMacdTrade(pool, prices, ps, i, j, k)
				
	pool.showStrategies()

def doMacdTrade(pool, prices, ps, fast, slow, sign):
	global highest, openLevel, closeLevel
	
	sname = 'MACD_' + str(fast) + '_' + str(slow) + '_' + str(sign)
	macds = macd.calc_macd(prices, fast, slow, sign)
	mas = ma.calc_ema(ps, slow)
	
	t = Trader(sname)
	for i in range(slow + sign, len(prices)):
		if macds['macd'][i] < 0 and macds['macd'][i] > macds['sign'][i] and macds['macd'][i-1] < macds['sign'][i-1] and abs(macds['macd'][i]) > openLevel and mas[i] > mas[i-1]:
			notes = 'macd under 0, and abs larger than openlevel'
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if macds['macd'][i] < 0 and macds['macd'][i] > macds['sign'][i] and macds['macd'][i-1] < macds['sign'][i-1] and abs(macds['macd'][i]) > closeLevel and mas[i] > mas[i-1]:
			notes = 'macd under 0, and abs larger than closelevel'
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes, True)
		
		if macds['macd'][i] > 0 and macds['macd'][i] < macds['sign'][i] and macds['macd'][i-1] > macds['sign'][i-1] and abs(macds['macd'][i]) > openLevel and mas[i] < mas[i-1]:
			notes = 'macd above 0, and abs larger than openlevel'
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
	
		if macds['macd'][i] > 0 and macds['macd'][i] < macds['sign'][i] and macds['macd'][i-1] > macds['sign'][i-1] and abs(macds['macd'][i]) > closeLevel and mas[i] < mas[i-1]:
			notes = 'macd above 0, and abs larger than closeLevel'
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes, True)
			
		t.show(prices[i]['date'], prices[i]['time'], prices[i]['rmb'])
	
	pool.estimate(t)
	return
	
