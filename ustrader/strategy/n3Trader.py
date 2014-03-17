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

mas = emas = smas = lwmas = std = prices = None

def runStrategy(in_prices):
	global mas, emas, smas, lwmas, std, prices
	log.debug('beginning one strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
	std = [0] * 51
	l = len(prices)
	for period in range(5, 41):
		std[period] = [0] * l
		for i in range(period - 1, l):
			std[period][i] = round(np.std(ps[i-period+1 : i+1], dtype=np.float64, ddof=0), 3)
	
	mas = [0] * 181
	emas = [0] * 181
	smas = [0] * 181
	lwmas = [0] * 181
	for period in range(2, 181):
		mas[period] = ma.calc_ma(ps, period)
		emas[period] = ma.calc_ema(ps, period)
		smas[period] = ma.calc_sma(ps, period)
		lwmas[period] = ma.calc_lwma(ps, period)
		
	
	#pool = StrategyPool(100)
	#t = doTrade(pool, 20, 0.1, 0.2, 'SMA', 20, 'SMA', 34, 'LWMA', 40, 'SMA', 20, 'SMA', 34, 'LWMA', 120, 'MA', 20, 'SMA', 34, 'LWMA', 120)
	#pool.showStrategies()
	#return 
	
	log.debug('running first strategy ...')
	starttime = time.time() 
	matypes = ['MA', 'EMA', 'SMA', 'LWMA']
	
	#farr = [2, 3, 4, 5, 6, 7, ]
	#s1arr = [4, 6, 8, 10, 12, 14, 16, 18, 20, ]
	#s2arr = [0, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, ]
	#farr = [20,]
	#s1arr = [40, ]
	#s2arr = [0, ]
	farr = range(40, 41)[::3]
	s1arr = range(4, 121)[::6]
	s2arr = range(0, 181)[::15]
	
	stdGuage1, stdGuage2 = 0.1, 0.2
	pool = StrategyPool(50)
	poola = StrategyPool(10)
	poolb = StrategyPool(10)
	poolc = StrategyPool(10)
	
	for stdPeriod in [20, ]:
		for no in ['A', 'B', 'C']:
			for ft, f in [(matype, period) for matype in matypes for period in farr]:
				for s1t, s1 in [(matype, period) for matype in matypes for period in s1arr]:
					if s1 < f: continue
					elapsed = long(time.time() - starttime)
					log.debug('== ' + str(elapsed) + ',' + ft + '_' + str(f) + ',' + s1t + '_' + str(s1) + ' ==')
					
					for s2t, s2 in [(matype, period) for matype in matypes for period in s2arr]:
						if s2 != 0 and s2 <= s1: continue
						if s2 == 0 and (s2t == 'EMA' or s2t == 'SMA' or s2t == 'LWMA'): continue
						if no == 'A':
							doTrade(poola, stdPeriod, stdGuage1, stdGuage2, ft, f, s1t, s1, s2t, s2, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0)
						elif no == 'B':
							doTrade(poolb, stdPeriod, stdGuage1, stdGuage2, '', 0, '', 0, '', 0, ft, f, s1t, s1, s2t, s2, '', 0, '', 0, '', 0)
						elif no == 'C':
							doTrade(poolc, stdPeriod, stdGuage1, stdGuage2, '', 0, '', 0, '', 0, '', 0, '', 0, '', 0, ft, f, s1t, s1, s2t, s2)
			elapsed = long(time.time() - starttime)
			log.info('find ' + no + ' time: ' + str(elapsed) + ' ')
		
		for i in range(10):
			sa = poola.strategies[i]
			sb = poolb.strategies[i]
			sc = poolc.strategies[i]
			t = doTrade(pool, stdPeriod, stdGuage1, stdGuage2, sa[0].args[0], sa[0].args[1], sa[0].args[2], sa[0].args[3], sa[0].args[4], sa[0].args[5], sb[0].args[6], sb[0].args[7], sb[0].args[8], sb[0].args[9], sb[0].args[10], sb[0].args[11], sc[0].args[12], sc[0].args[13], sc[0].args[14], sc[0].args[15], sc[0].args[16], sc[0].args[17])
			#t.generateGraph()
	
	pool.showStrategies()
	
def doTrade(pool, stdPeriod, stdGuage1, stdGuage2, aft, af, as1t, as1, as2t, as2, bft, bf, bs1t, bs1, bs2t, bs2, cft, cf, cs1t, cs1, cs2t, cs2):
	global std, prices
	
	sname = str(stdPeriod) + '_' + str(stdGuage1) + '_' + str(stdGuage2)
	sname += '_' + aft + '_' + str(af) + '_' + as1t + '_' + str(as1) + '_' + as2t + '_' + str(as2)
	sname += '_' + bft + '_' + str(bf) + '_' + bs1t + '_' + str(bs1) + '_' + bs2t + '_' + str(bs2)
	sname += '_' + cft + '_' + str(cf) + '_' + cs1t + '_' + str(cs1) + '_' + cs2t + '_' + str(cs2)
	
	afma, as1ma, as2ma = getMas(aft, af), getMas(as1t, as1), getMas(as2t, as2)
	bfma, bs1ma, bs2ma = getMas(bft, bf), getMas(bs1t, bs1), getMas(bs2t, bs2)
	cfma, cs1ma, cs2ma = getMas(cft, cf), getMas(cs1t, cs1), getMas(cs2t, cs2)
	
	front = max(as1, as2, bs1, bs2, cs1, cs2)
	
	t = Trader(sname)
	t.args = [aft, af, as1t, as1, as2t, as2, bft, bf, bs1t, bs1, bs2t, bs2, cft, cf, cs1t, cs1, cs2t, cs2]
	for i in range(front, len(prices)):
		price = prices[i]
		
		if std[stdPeriod][i] > stdGuage2:
			t.switchActiveCounter(2, price['dt'], price['rmb'])
		elif std[stdPeriod][i] > stdGuage1:
			t.switchActiveCounter(1, price['dt'], price['rmb'])
		else:
			t.switchActiveCounter(3, price['dt'], price['rmb'])
			
		for cntNo in range(3):
			if cntNo == 0: fma, s1, s1ma, s2, s2ma = afma, as1, as1ma, as2, as2ma
			if cntNo == 1: fma, s1, s1ma, s2, s2ma = bfma, bs1, bs1ma, bs2, bs2ma
			if cntNo == 2: fma, s1, s1ma, s2, s2ma = cfma, cs1, cs1ma, cs2, cs2ma
			
			if s1 == 0 and s2 == 0: continue
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
				
			t.processOrder(price['dt'], price['rmb'], volume, cntNo=cntNo, notes=notes)
		
	pool.estimate(t)
	return t
	
def getMas(matype, period):
	global mas, emas, smas, lwmas
	
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
	