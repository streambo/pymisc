# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import balLogger as logb
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool

mas = emas = smas = std = prices = None

def runStrategy(in_prices):
	global mas, emas, smas, std, prices
	log.debug('beginning first strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
	std = [0] * 51
	l = len(prices)
	for period in range(2, 51):
		std[period] = [0] * l
		for i in range(period - 1, l):
			std[period][i] = round(np.std(ps[i-period+1 : i+1], dtype=np.float64, ddof=0), 3)
		
	mas = [0] * 61
	emas = [0] * 61
	smas = [0] * 61
	for period in range(2, 61):
		mas[period] = ma.calc_ma(ps, period)
		emas[period] = ma.calc_ema(ps, period)
		smas[period] = ma.calc_sma(ps, period)
		
	pool = StrategyPool(100)
	#t = doTrade(pool, 25, 1.0, 'MA', 7, 'SMA', 12, 'EMA', 31, 'SMA', 7, 'MA', 12, 'MA', 13)
	t = doTrade(pool, 25, 1.3, 'MA', 7, 'SMA', 13, 'EMA', 31, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.0, 'MA', 7, 'SMA', 13, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.0, 'MA', 7, 'SMA', 12, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 13)
	#
	#t = doTrade(pool, 25, 1.1, 'MA', 7, 'SMA', 12, 'EMA', 31, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.1, 'MA', 7, 'SMA', 13, 'EMA', 31, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.1, 'MA', 7, 'SMA', 13, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.1, 'MA', 7, 'SMA', 12, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 13)
	#
	#t = doTrade(pool, 25, 1.2, 'MA', 7, 'SMA', 12, 'EMA', 31, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.2, 'MA', 7, 'SMA', 13, 'EMA', 31, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.2, 'MA', 7, 'SMA', 13, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.2, 'MA', 7, 'SMA', 12, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 13)
	#
	#t = doTrade(pool, 25, 1.3, 'MA', 7, 'SMA', 12, 'EMA', 31, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.3, 'MA', 7, 'SMA', 13, 'EMA', 31, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.3, 'MA', 7, 'SMA', 13, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.3, 'MA', 7, 'SMA', 12, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 13)
	#t = doTrade(pool, 25, 1.0, 'MA', 7, 'SMA', 13, 'EMA', 26, 'SMA', 7, 'MA', 12, 'MA', 12)
	pool.showStrategies()
		
	return 
	
	log.debug('running first strategy ...')
	starttime = datetime.datetime.now() 
	matypes = ['MA', 'EMA', 'SMA']
	
	#farr = [2, 3, 4, 5, 6, 7, ]
	#s1arr = [4, 6, 8, 10, 12, 14, 16, 18, 20, ]
	#s2arr = [0, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, ]
	
	farr = [2,]
	s1arr = [4, ]
	s2arr = [0, ]
	
	pool = StrategyPool(100)
	for stdPeriod in [20, ]:
		stdGuage = 0.5
		for stdGuage in [1.3, ]:
			maxAEquity = maxBEquity = 0
			poola = StrategyPool(5)
			poolb = StrategyPool(5)
			
			for ft, f in [(matype, period) for matype in matypes for period in farr]:
				for s1t, s1 in [(matype, period) for matype in matypes for period in s1arr]:
					elapsed = (datetime.datetime.now() - starttime).seconds
					log.debug('== ' + str(elapsed) + ',' + ft + '_' + str(f) + ',' + s1t + '_' + str(s1) + ' ==')
					for s2t, s2 in [(matype, period) for matype in matypes for period in s2arr]:
						if s2 != 0 and s2 < s1: continue
						if s2 == 0 and (s2t == 'EMA' or s2t == 'SMA'): continue
						
						t = doTrade(poola, stdPeriod, stdGuage, ft, f, s1t, s1, s2t, s2, '', 0, '', 0, '', 0)
						
						if t.equity > maxAEquity:
							maxAEquity = t.equity
							maxEAs = [ft, f, s1t, s1, s2t, s2]
						
			elapsed = (datetime.datetime.now() - starttime).seconds
			log.info('find A time: ' + str(elapsed) + ' ')
			#poola.showStrategies()
			
			for ft, f in [(matype, period) for matype in matypes for period in farr]:
				for s1t, s1 in [(matype, period) for matype in matypes for period in s1arr]:
					elapsed = (datetime.datetime.now() - starttime).seconds
					log.debug('== ' + str(elapsed) + ',' + ft + '_' + str(f) + ',' + s1t + '_' + str(s1) + ' ==')
					for s2t, s2 in [(matype, period) for matype in matypes for period in s2arr]:
						if s2 != 0 and s2 < s1: continue
						if s2 == 0 and (s2t == 'EMA' or s2t == 'SMA'): continue
						
						t = doTrade(poolb, stdPeriod, stdGuage, '', 0, '', 0, '', 0, ft, f, s1t, s1, s2t, s2)
						
						if t.equity > maxBEquity:
							maxBEquity = t.equity
							maxEBs = [ft, f, s1t, s1, s2t, s2]
						
			elapsed = (datetime.datetime.now() - starttime).seconds
			log.info('find B time: ' + str(elapsed) + ' ')
			#poolb.showStrategies()
			
			logb.info(str(stdPeriod) + ',' + str(stdGuage) + ',' + str(maxAEquity) + ',' + str(maxBEquity))
			logb.info(str(maxEAs))
			logb.info(str(maxEBs))
			
			for i in range(5):
				sa = poola.strategies[i]
				sb = poolb.strategies[i]
				t = doTrade(pool, stdPeriod, stdGuage, sa[0].args[2], sa[0].args[3], sa[0].args[4], sa[0].args[5], sa[0].args[6], sa[0].args[7], sb[0].args[8], sb[0].args[9], sb[0].args[10], sb[0].args[11], sb[0].args[12], sb[0].args[13])
				t.generateGraph()
				#pool.estimate(t)
				
			#stdGuage += 0.1
	
	pool.showStrategies()
	
	
def doTrade(pool, stdPeriod, stdGuage, afmt, af, as1mt, as1, as2mt, as2, bfmt, bf, bs1mt, bs1, bs2mt, bs2):
	global std, prices
	
	sname = str(stdPeriod) + '_' + str(stdGuage)
	sname += '_' + afmt + '_' + str(af) + '_' + as1mt + '_' + str(as1)
	if as2 > 0: sname += '_' + as2mt + '_' + str(as2)
	sname +=  '_' + bfmt + '_' + str(bf) + '_' + bs1mt + '_' +str(bs1)
	if bs2 > 0: sname += '_' + bs2mt + '_' + str(bs2)
	
	afma, as1ma, as2ma = getMas(afmt, af), getMas(as1mt, as1), getMas(as2mt, as2)
	bfma, bs1ma, bs2ma = getMas(bfmt, bf), getMas(bs1mt, bs1), getMas(bs2mt, bs2)
	
	front = max(as1, as2, bs1, bs2)
	
	t = Trader(sname)
	t.args = [stdPeriod, stdGuage, afmt, af, as1mt, as1, as2mt, as2, bfmt, bf, bs1mt, bs1, bs2mt, bs2]
	for i in range(front, len(prices)):
		price = prices[i]
		if std[stdPeriod][i] > stdGuage:
			t.switchActiveCounter(1, price['dt'], price['rmb'])
		else:
			t.switchActiveCounter(0, price['dt'], price['rmb'])
			
		#if std[stdPeriod][i] > 1.3:
		#	t.switchActiveCounter(1, price['dt'], price['rmb'])
		#elif std[stdPeriod][i] > stdGuage:
		#	t.switchActiveCounter(0, price['dt'], price['rmb'])
		#else:
		#	t.switchActiveCounter(2, price['dt'], price['rmb'])
		volume = 0
		notes = ''
		if as1 > 0 and afma[i - 1] <= as1ma[i - 1] and afma[i] > as1ma[i]:
			notes += 'af>as1;' + str(afma[i - 1]) + ';' + str(as1ma[i - 1]) + ';' + str(afma[i]) + ';' + str(as1ma[i]) + ';'
			volume += 1
		
		if as1 > 0 and afma[i - 1] >= as1ma[i - 1] and afma[i] < as1ma[i]:
			notes += 'af<as1;' + str(afma[i - 1]) + ';' + str(as1ma[i - 1]) + ';' + str(afma[i]) + ';' + str(as1ma[i]) + ';'
			volume += -1
		
		if as2 > 0 and afma[i - 1] <= as2ma[i - 1] and afma[i] > as2ma[i]:
			notes += 'af>as2;' + str(afma[i - 1]) + ';' + str(as2ma[i - 1]) + ';' + str(afma[i]) + ';' + str(as2ma[i]) + ';'
			volume += 1
		
		if as2 > 0 and afma[i - 1] >= as2ma[i - 1] and afma[i] < as2ma[i]:
			notes += 'af<as2;' + str(afma[i - 1]) + ';' + str(as2ma[i - 1]) + ';' + str(afma[i]) + ';' + str(as2ma[i]) + ';'
			volume += -1
		
		t.processOrder(price['dt'], price['rmb'], volume * 1000, cntNo=0, notes=notes)
		volume = 0
		notes = ''
		
		if bs1 > 0 and bfma[i - 1] <= bs1ma[i - 1] and bfma[i] > bs1ma[i]:
			notes += 'bf>bs1;' + str(bfma[i - 1]) + ';' + str(bs1ma[i - 1]) + ';' + str(bfma[i]) + ';' + str(bs1ma[i]) + ';'
			volume += 1
		
		if bs1 > 0 and bfma[i - 1] >= bs1ma[i - 1] and bfma[i] < bs1ma[i]:
			notes += 'bf<bs1,' + str(bfma[i - 1]) + ';' + str(bs1ma[i - 1]) + ';' + str(bfma[i]) + ';' + str(bs1ma[i]) + ';'
			volume += -1
		
		if bs2 > 0 and bfma[i - 1] <= bs2ma[i - 1] and bfma[i] > bs2ma[i]:
			notes += 'bf>bs2;' + str(bfma[i - 1]) + ';' + str(bs2ma[i - 1]) + ';' + str(bfma[i]) + ';' + str(bs2ma[i]) + ';'
			volume += 1
		
		if bs2 > 0 and bfma[i - 1] >= bs2ma[i - 1] and bfma[i] < bs2ma[i]:
			notes += 'bf<bs2;' + str(bfma[i - 1]) + ';' + str(bs2ma[i - 1]) + ';' + str(bfma[i]) + ';' + str(bs2ma[i])
			volume += -1
		
		t.processOrder(price['dt'], price['rmb'], volume * 1000, cntNo=1, notes=notes)
		
	pool.estimate(t)
	print t.stats['equity']
	return t
		
def getMas(matype, period):
	global mas, emas, smas
	
	if matype == 'MA':
		return mas[period]
	elif matype == 'EMA':
		return emas[period]
	elif matype == 'SMA':
		return smas[period]
	else:
		return None


def runStrategy_0(in_prices):
	global mas, emas, smas, std, prices
	log.debug('beginning first strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
	std = [0] * 51
	l = len(prices)
	for period in range(2, 51):
		std[period] = [0] * l
		for i in range(period - 1, l):
			std[period][i] = round(np.std(ps[i-period+1 : i+1], dtype=np.float64, ddof=0), 3)
		
	mas = [0] * 61
	emas = [0] * 61
	smas = [0] * 61
	for period in range(2, 61):
		mas[period] = ma.calc_ma(ps, period)
		emas[period] = ma.calc_ema(ps, period)
		smas[period] = ma.calc_sma(ps, period)
	
	log.debug('running first strategy ...')
	starttime = datetime.datetime.now() 
	matypes = ['MA', 'EMA', 'SMA']
	
	farr = [2, 3, 4, 5, 6, 7, ]
	s1arr = [4, 6, 8, 10, 12, 14, 16, 18, 20, ]
	s2arr = [0, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, ]
	
	pool = StrategyPool(100)
	
	for stdPeriod in [20, 30, 40]:
		stdGuage = 1.0
		while stdGuage <= 1.3:
			maxAEquity = maxBEquity = 0
			poola = StrategyPool(5)
			poolb = StrategyPool(5)
			
			for ft, f in [(matype, period) for matype in matypes for period in farr]:
				for s1t, s1 in [(matype, period) for matype in matypes for period in s1arr]:
					elapsed = (datetime.datetime.now() - starttime).seconds
					log.debug('== ' + str(elapsed) + ',' + ft + '_' + str(f) + ',' + s1t + '_' + str(s1) + ' ==')
					for s2t, s2 in [(matype, period) for matype in matypes for period in s2arr]:
						if s2 != 0 and s2 < s1: continue
						if s2 == 0 and (s2t == 'EMA' or s2t == 'SMA'): continue
						
						t = doTrade(poola, stdPeriod, stdGuage, ft, f, s1t, s1, s2t, s2, '', 0, '', 0, '', 0)
						
						if t.equity > maxAEquity:
							maxAEquity = t.equity
							maxEAs = [ft, f, s1t, s1, s2t, s2]
						
			elapsed = (datetime.datetime.now() - starttime).seconds
			log.info('find A time: ' + str(elapsed) + ' ')
			poola.showStrategies()
			
			for ft, f in [(matype, period) for matype in matypes for period in farr]:
				for s1t, s1 in [(matype, period) for matype in matypes for period in s1arr]:
					elapsed = (datetime.datetime.now() - starttime).seconds
					log.debug('== ' + str(elapsed) + ',' + ft + '_' + str(f) + ',' + s1t + '_' + str(s1) + ' ==')
					for s2t, s2 in [(matype, period) for matype in matypes for period in s2arr]:
						if s2 != 0 and s2 < s1: continue
						if s2 == 0 and (s2t == 'EMA' or s2t == 'SMA'): continue
						
						t = doTrade(poolb, stdPeriod, stdGuage, '', 0, '', 0, '', 0, ft, f, s1t, s1, s2t, s2)
						
						if t.equity > maxBEquity:
							maxBEquity = t.equity
							maxEBs = [ft, f, s1t, s1, s2t, s2]
						
			elapsed = (datetime.datetime.now() - starttime).seconds
			log.info('find B time: ' + str(elapsed) + ' ')
			poolb.showStrategies()
			
			logb.info(str(stdPeriod) + ',' + str(stdGuage) + ',' + str(maxAEquity) + ',' + str(maxBEquity))
			logb.info(str(maxEAs))
			logb.info(str(maxEBs))
			
			for i in range(5):
				sa = poola.strategies[i]
				sb = poolb.strategies[i]
				t = doTrade(pool, stdPeriod, stdGuage, sa[0].args[2], sa[0].args[3], sa[0].args[4], sa[0].args[5], sa[0].args[6], sa[0].args[7], sb[0].args[8], sb[0].args[9], sb[0].args[10], sb[0].args[11], sb[0].args[12], sb[0].args[13])
				t.generateGraph()
				pool.estimate(t)
				
			stdGuage += 0.1
	
	pool.showStrategies()
	

def runStrategy_1(in_prices):
	global mas, emas, smas, std, prices
	log.debug('beginning first strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
	std = [0] * 51
	l = len(prices)
	for period in range(2, 51):
		std[period] = [0] * l
		for i in range(period - 1, l):
			std[period][i] = round(np.std(ps[i-period+1 : i+1], dtype=np.float64, ddof=0), 3)
		
	mas = [0] * 61
	emas = [0] * 61
	smas = [0] * 61
	for period in range(2, 61):
		mas[period] = ma.calc_ma(ps, period)
		emas[period] = ma.calc_ema(ps, period)
		smas[period] = ma.calc_sma(ps, period)
	
	log.debug('running first strategy ...')
	starttime = datetime.datetime.now() 
	
	strat_as = [
['MA',6,'SMA',14,'EMA',39],
['MA',7,'SMA',10,'SMA',12],
['MA',7,'SMA',12,'EMA',18],
['MA',7,'SMA',12,'MA',27],
['MA',7,'SMA',12,'SMA',12],
['MA',7,'SMA',14,'EMA',27],
['MA',7,'SMA',14,'EMA',30],
['MA',7,'SMA',14,'EMA',33],
['MA',7,'SMA',14,'EMA',45],
['MA',7,'SMA',14,'MA',27],
['MA',7,'SMA',14,'SMA',15],
['MA',7,'SMA',14,'SMA',30],
['MA',7,'SMA',16,'EMA',24],
['MA',7,'SMA',16,'EMA',27],
['MA',7,'SMA',16,'EMA',30],
['MA',7,'SMA',16,'MA',30]
]
	strat_bs = [
['EMA',3,'EMA',16,'MA',42],
['EMA',3,'EMA',16,'MA',45],
['EMA',6,'SMA',6,'MA',30 ],
['EMA',7,'MA',4,'EMA',51 ],
['MA',6,'SMA',16,'EMA',45],
['MA',6,'SMA',18,'MA',36 ],
['MA',6,'SMA',20,'MA',36 ],
['MA',6,'SMA',20,'MA',39 ],
['MA',7,'EMA',18,'EMA',45],
['MA',7,'SMA',12,'EMA',42],
['MA',7,'SMA',12,'SMA',21],
['MA',7,'SMA',14,'EMA',42],
['MA',7,'SMA',14,'MA',45 ],
['MA',7,'SMA',14,'SMA',21],
['SMA',2,'EMA',16,'MA',42],
['SMA',4,'MA',4,'EMA',51 ],
['SMA',5,'MA',4,'MA',15  ],
['SMA',5,'MA',6,'MA',42  ],
['SMA',6,'EMA',10,'MA',36],
['SMA',6,'MA',12,'MA',12 ],
['SMA',7,'MA',12,'EMA',18],
['SMA',7,'MA',12,'EMA',27],
['SMA',7,'MA',12,'EMA',36],
['SMA',7,'MA',12,'EMA',45],
['SMA',7,'MA',12,'EMA',48],
['SMA',7,'MA',12,'MA',12 ],
['SMA',7,'MA',12,'MA',18 ],
['SMA',7,'MA',12,'MA',33 ],
['SMA',7,'MA',12,'MA',36 ],
['SMA',7,'MA',12,'MA',51 ],
['SMA',7,'MA',12,'SMA',15]
]
	
	pool = StrategyPool(100)
	for stdPeriod in [5, 8, 10, 12, 15, 18, 19, 20, 21, 22, 25, 30, 32, 34, 38, 40]:
		stdGuage = 0.6
		while stdGuage <= 2:
			elapsed = (datetime.datetime.now() - starttime).seconds
			log.debug('== ' + str(elapsed) + ',' + str(stdPeriod) + ',' + str(stdGuage) + ' ==')
			
			for sa in strat_as:
				for sb in strat_bs:
					doTrade(pool, stdPeriod, stdGuage, sa[0], sa[1], sa[2], sa[3], sa[4], sa[5], sb[0], sb[1], sb[2], sb[3], sb[4], sb[5])
			
			stdGuage += 0.1
		
	pool.showStrategies()
	
	return
	

def runStrategy_2(in_prices):
	global mas, emas, smas, std, prices
	log.debug('beginning first strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
	std = [0] * 51
	l = len(prices)
	for period in range(2, 51):
		std[period] = [0] * l
		for i in range(period - 1, l):
			std[period][i] = round(np.std(ps[i-period+1 : i+1], dtype=np.float64, ddof=0), 3)
		
	mas = [0] * 61
	emas = [0] * 61
	smas = [0] * 61
	for period in range(2, 61):
		mas[period] = ma.calc_ma(ps, period)
		emas[period] = ma.calc_ema(ps, period)
		smas[period] = ma.calc_sma(ps, period)
	
	log.debug('running first strategy ...')
	starttime = datetime.datetime.now() 
	
	strat_as = [
['MA',7,'SMA',10,'SMA',12],
['MA',7,'SMA',14,'EMA',33],
['MA',7,'SMA',16,'EMA',27],
]
	strat_bs = [
['SMA',7,'MA',12,'MA',12 ],
['SMA',7,'MA',12,'MA',36 ],
['MA',7,'SMA',14,'EMA',33],
]
	
	pool = StrategyPool(100)
	
	for stdPeriod in [25]:
		stdGuage = 1.3
		while stdGuage <= 1.3:
			elapsed = (datetime.datetime.now() - starttime).seconds
			log.debug('== ' + str(elapsed) + ',' + str(stdPeriod) + ',' + str(stdGuage) + ' ==')
			
			for sa in strat_as:
				for sb in strat_bs:
					doTrade(pool, stdPeriod, stdGuage, sa[0], sa[1], sa[2], sa[3], sa[4], sa[5], sb[0], sb[1], sb[2], sb[3], sb[4], sb[5])
			
			stdGuage += 0.02
		
	pool.showStrategies()
	
	return
	