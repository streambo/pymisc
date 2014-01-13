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
	
	#doMaTrade(prices, ps, 'EMA', 6, 14, 24, result = True)
	#return
	
	for i in range(2, 9):
		for j in range(6, 20):
			if i >= j: continue
			doMaTrade(prices, ps, 'MA', i, j)
			doMaTrade(prices, ps, 'EMA', i, j)
			doMaTrade(prices, ps, 'SMA', i, j)
			
			for k in range(10, 40):
				if j >= k: continue
				doMaTrade(prices, ps, 'MA', i, j, k)
				doMaTrade(prices, ps, 'EMA', i, j, k)
				doMaTrade(prices, ps, 'SMA', i, j, k)
				
				#for l in range(10, 60):
				#	if k >= l: continue
				#	doMaTrade(prices, ps, 'MA', i, j, k, l)
				#	doMaTrade(prices, ps, 'EMA', i, j, k, l)
				#	doMaTrade(prices, ps, 'SMA', i, j, k, l)

def doMaTrade(prices, ps, matype, fast, slow, slow2 = 0, slow3 = 0, result = False):
	global highest
	
	sname = matype + '_' + str(fast) + '_' + str(slow) 
	if slow2 > 0: sname += '_' + str(slow2)
	if slow3 > 0: sname += '_' + str(slow3)
	
	if matype == 'MA':
		maMethod = ma.calc_ma
	elif matype == 'EMA':
		maMethod = ma.calc_ema
	elif matype == 'SMA':
		maMethod = ma.calc_sma
	
	maf = maMethod(ps, fast)
	mas = maMethod(ps, slow)
	if slow2 > 0:
		mas2 = maMethod(ps, slow2)
	if slow3 > 0:
		mas3 = maMethod(ps, slow3)
	
	t = Trader(sname)
	for i in range(max(slow, slow2, slow3), len(prices)):
		if maf[i - 1] < mas[i - 1] and maf[i] >= mas[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas: ' + str(mas[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas: ' + str(mas[i])
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if slow2 >0 and maf[i - 1] < mas2[i - 1] and maf[i] >= mas2[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas2: ' + str(mas2[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas2: ' + str(mas2[i])
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if slow3 >0 and maf[i - 1] < mas3[i - 1] and maf[i] >= mas3[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas3: ' + str(mas3[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas3: ' + str(mas3[i])
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if maf[i - 1] > mas[i - 1] and maf[i] <= mas[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas: ' + str(mas[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas: ' + str(mas[i])
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
		
		if slow3 >0 and maf[i - 1] > mas3[i - 1] and maf[i] <= mas3[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas2: ' + str(mas3[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas3: ' + str(mas3[i])
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
		
		t.show(prices[i]['date'], prices[i]['time'], prices[i]['rmb'])
	
	if t.equity > highest or result:
		highest = t.equity
		logs.info(sname + ',' + str(len(t.bbuyDates)) + ',' + str(len(t.bsellDates)) + ',' + str(t.equity))
		t.generateGraph()

