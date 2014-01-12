# -*- coding: utf-8 -*-
import datetime, time, csv, os
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj


def runStrategy(table):
	logs.info('STRATEGY,BUY TIMES, SELL TIMES, FINAL EQUITY')
	
	prices = SqliteDB().getAllPrices(table)
	ps = [p['close'] for p in prices]
	
	for i in range(2, 9):
		for j in range(6, 20):
			for k in range(10, 40):
				if i >= j or j >= k: continue
				doMas(prices, ps, 'MA', i, j, k)
				doMas(prices, ps, 'EMA', i, j, k)
				doMas(prices, ps, 'SMA', i, j, k)

def doMas(prices, ps, matype, fast, slow, supply):
	
	sname = matype + '_' + str(fast) + '_' + str(slow) + '_' + str(supply)
	if matype == 'MA':
		maMethod = ma.calc_ma
	elif matype == 'EMA':
		maMethod = ma.calc_ema
	elif matype == 'SMA':
		maMethod = ma.calc_sma
	
	maf = maMethod(ps, fast)
	mas = maMethod(ps, slow)
	mas2 = maMethod(ps, supply)
	
	t = Trader(sname)
	for i in range(slow, len(prices)):
		if maf[i - 1] < mas[i - 1] and maf[i] >= mas[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas: ' + str(mas[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas: ' + str(mas[i])
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if maf[i - 1] < mas2[i - 1] and maf[i] >= mas2[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas2: ' + str(mas2[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas2: ' + str(mas2[i])
			t.buy(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
			
		if maf[i - 1] > mas[i - 1] and maf[i] <= mas[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas: ' + str(mas[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas: ' + str(mas[i])
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
		
		if maf[i - 1] > mas2[i - 1] and maf[i] <= mas2[i]:
			notes = 'LAST maf: ' + str(maf[i - 1]) + ';mas2: ' + str(mas2[i - 1]) + 'CURRENT maf: ' + str(maf[i]) + ';mas2: ' + str(mas2[i])
			t.sell(prices[i]['date'], prices[i]['time'], prices[i]['rmb'], notes)
		
		t.show(prices[i]['date'], prices[i]['time'], prices[i]['rmb'])
	
	logs.info(sname + ',' + str(len(t.bbuyDates)) + ',' + str(len(t.bsellDates)) + ',' + str(t.equity))
	t.generateGraph()

