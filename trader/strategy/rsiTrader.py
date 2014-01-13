# -*- coding: utf-8 -*-
import datetime, time, csv, os
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj

highest = 0

def runStrategy(prices):
	logs.info('STRATEGY,BUY TIMES, SELL TIMES, FINAL EQUITY')
	
	#prices = SqliteDB().getAllPrices(table)
	ps = [p['close'] for p in prices]
	
	doRSITrade(prices, 14, 90, 10)
	return
	
	for i in range(3, 30):
		for j in range(70, 100):
			for k in range(1, 31):
				doRSITrade(prices, ps, i, j, k)
	
	
def doRSITrade(prices, ps, period, up, down):
	global highest
	
	sname = 'RSI_' + str(period) + '_' + str(up) + '_' + str(down)
	rsis = rsi.calc_rsi(prices, period)
	t = Trader(sname)
	
	for i in range(period, len(prices)):
		if rsis['rsi'][i] <= down:
			notes = 'RSI : ' + str(rsis['rsi'][i]) + ';down: ' + str(down)
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if rsis['rsi'][i] >= up:
			notes = 'RSI : ' + str(rsis['rsi'][i]) + ';up: ' + str(up)
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
		
		t.show(prices[i]['date'], prices[i]['time'], prices[i]['rmb'])
	
	if t.equity > highest:
		highest = t.equity
	logs.info(sname + ',' + str(len(t.bbuyDates)) + ',' + str(len(t.bsellDates)) + ',' + str(t.equity))
	t.generateGraph()
	