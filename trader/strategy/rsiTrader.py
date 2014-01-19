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
	
	doRSITrade(pool, prices, 14, 70, 30)
	pool.showStrategies()
	return
	
	for i in range(3, 30):
		for j in range(70, 100):
			for k in range(1, 31):
				doRSITrade(pool, prices, i, j, k)
	
	
def doRSITrade(pool, prices, period, up, down):
	global highest
	
	sname = 'RSI_' + str(period) + '_' + str(up) + '_' + str(down)
	rsis = rsi.calc_rsi(prices, period)
	t = Trader(sname)
	
	for i in range(period, len(prices)):
		if rsis['rsi'][i] < down and rsis['rsi'][i-1] >= down:
			notes = 'RSI: ' + str(rsis['rsi'][i]) + ';pre: ' + str(rsis['rsi'][i-1]) + ';down: ' + str(down)
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if rsis['rsi'][i] >= down and rsis['rsi'][i - 1] < down:
			notes = 'RSI: ' + str(rsis['rsi'][i]) + ';pre: ' + str(rsis['rsi'][i-1]) + ';down: ' + str(down)
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes, True)
		
		if rsis['rsi'][i] > up and rsis['rsi'][i-1] <= up:
			notes = 'RSI: ' + str(rsis['rsi'][i]) + ';pre: ' + str(rsis['rsi'][i-1]) + ';up: ' + str(up)
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if rsis['rsi'][i] <= up and rsis['rsi'][i-1] > up:
			notes = 'RSI: ' + str(rsis['rsi'][i]) + ';pre: ' + str(rsis['rsi'][i-1]) + ';up: ' + str(up)
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes, True)
		
		t.show(prices[i]['date'], prices[i]['time'], prices[i]['rmb'])
	
	pool.estimate(t)
	
	