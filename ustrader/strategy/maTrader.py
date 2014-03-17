# -*- coding: utf-8 -*-
import datetime, time, csv, os
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool

mas = emas = smas = lwmas = prices = None

def runStrategy(in_prices):
	global mas, emas, smas, lwmas, prices
	log.debug('beginning ma strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
	log.debug('generating mas ...')
	mas = [0] * 61
	emas = [0] * 61
	smas = [0] * 61
	lwmas = [0] * 61
	for period in range(2, 61):
		mas[period] = ma.calc_ma(ps, period)
		emas[period] = ma.calc_ema(ps, period)
		smas[period] = ma.calc_sma(ps, period)
		lwmas[period] = ma.calc_lwma(ps, period)
	
	pool = StrategyPool(20)
	doMaTrade(pool, 'SMA', 19, 'MA', 40, 'LWMA', 60)
	pool.showStrategies()
	return
	
	log.debug('running ma strategy ...')
	starttime = datetime.datetime.now() 
	matypes = ['MA', 'EMA', 'SMA', 'LWMA']
	pool = StrategyPool(100)
	
	for ft, f in [(matype, period) for matype in matypes for period in range(2, 10)]:
		for s1t, s1 in [(matype, period) for matype in matypes for period in range(4, 21)]:
			elapsed = (datetime.datetime.now() - starttime).seconds
			log.debug('== ' + str(elapsed) + ',' + ft + '_' + str(f) + ',' + s1t + '_' + str(s1) + ' ==')
			for s2t, s2 in [(matype, period) for matype in matypes for period in range(0, 41)]:
				if s2 != 0 and s2 <= s1: continue
				if s2 == 0 and (s2t == 'EMA' or s2t == 'SMA' or s2t == 'LWMA'): continue
				doMaTrade(pool, ft, f, s1t, s1, s2t, s2)
	
	pool.showStrategies()
	
def doMaTrade(pool, ft, f, s1t, s1, s2t, s2):
	global prices
	
	sname = ft + '_' + str(f) + '_' + s1t + '_' + str(s1) + '_' + s2t + '_' + str(s2)
	fma, s1ma, s2ma = getMas(ft, f), getMas(s1t, s1), getMas(s2t, s2)
	
	t = Trader(sname)
	#t.args = [ft, f, s1t, s1, s2t, s2]
	front = max(s1, s2)
	for i in range(front, len(prices)):
		price = prices[i]
		volume = 0
		notes = ''
		if s1 > 0 and fma[i - 1] <= s1ma[i - 1] and fma[i] > s1ma[i]:
			notes += 'f>s1;' + str(fma[i - 1]) + ';' + str(s1ma[i - 1]) + ';' + str(fma[i]) + ';' + str(s1ma[i]) + ';'
			volume += 1
		
		if s1 > 0 and fma[i - 1] >= s1ma[i - 1] and fma[i] < s1ma[i]:
			notes += 'f<s1;' + str(fma[i - 1]) + ';' + str(s1ma[i - 1]) + ';' + str(fma[i]) + ';' + str(s1ma[i]) + ';'
			volume -= 1
		
		if s2 > 0 and fma[i - 1] <= s2ma[i - 1] and fma[i] > s2ma[i]:
			notes += 'f>s2;' + str(fma[i - 1]) + ';' + str(s2ma[i - 1]) + ';' + str(fma[i]) + ';' + str(s2ma[i]) + ';'
			volume += 1
		
		if s2 > 0 and fma[i - 1] >= s2ma[i - 1] and fma[i] < s2ma[i]:
			notes += 'f<s2;' + str(fma[i - 1]) + ';' + str(s2ma[i - 1]) + ';' + str(fma[i]) + ';' + str(s2ma[i]) + ';'
			volume -= 1
			
		t.processOrder(price['dt'], price['rmb'], volume, cntNo=0, notes=notes)
		
	pool.estimate(t)
	
def getMas(matype, period):
	global mas, emas, smas
	
	if matype == 'MA':
		return mas[period]
	elif matype == 'EMA':
		return emas[period]
	elif matype == 'SMA':
		return smas[period]
	elif matype == 'LWMA':
		return lwmas[period]
	else:
		return None
