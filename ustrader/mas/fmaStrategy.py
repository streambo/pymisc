# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import balLogger as logb
from strader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from mas.maPool import Pool

prices = ps = None

def runStrategy(in_prices):
	global prices, ps
	log.debug('beginning fma strategy ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
#12_0.15_SMA_31_EMA_56_SMA_160__0__0,93,93,1558,25166.84
#12_0.15_SMA_25_LWMA_48_SMA_160__0__0,105,97,1987,25156.73
#12_0.15_SMA_30_EMA_58_SMA_160__0__0,96,95,1558,24957.8
#36_0.15_SMA_31_EMA_56_SMA_160__0__0,92,87,1935,23762.4
#24_0.2_SMA_37_LWMA_64_SMA_140__0__0,92,86,1452,24911.19
#12_0.15__0__0_SMA_35_SMA_78_SMA_120,75,69,4941,24376.28
#12_0.15__0__0_MA_30_SMA_78_SMA_100,93,83,4376,24252.22
#12_0.15__0__0_SMA_35_SMA_72_SMA_120,77,71,4930,24391.03
#12_0.15__0__0_SMA_39_SMA_72_SMA_120,77,70,4946,24365.99
#36_0.15__0__0_EMA_17_LWMA_24_SMA_150,276,282,3205,24670.78
#24_0.2__0__0_SMA_9_MA_16_SMA_170,216,219,3667,24692.56
	pool = Pool(10)
	doTrade(pool, 12, 0.15, 'SMA', 25, 'LWMA', 48, 'SMA', 160, 'SMA', 35, 'SMA', 78, 'SMA', 120)
	doTrade(pool, 12, 0.15, 'SMA', 25, 'LWMA', 48, 'SMA', 160, 'MA', 30, 'SMA', 78, 'SMA', 100)
	doTrade(pool, 12, 0.15, 'SMA', 31, 'EMA', 56, 'SMA', 160, 'SMA', 35, 'SMA', 72, 'SMA', 120)
	doTrade(pool, 12, 0.15, 'SMA', 31, 'EMA', 56, 'SMA', 160, 'MA', 30, 'SMA', 78, 'SMA', 100)
	doTrade(pool, 36, 0.15, 'SMA', 31, 'EMA', 56, 'SMA', 160, 'EMA', 17, 'LWMA', 24, 'SMA', 150)
	doTrade(pool, 24, 0.2, 'SMA', 37, 'LWMA', 64, 'SMA', 140, 'SMA', 9, 'MA', 16, 'SMA', 170)
	pool.showStrategies()
	return 
	
	
def doTrade(pool, stdPeriod, stdGuage, afmt, af, as1mt, as1, as2mt, as2, bfmt, bf, bs1mt, bs1, bs2mt, bs2):
	
	sname = str(stdPeriod) + '_' + str(stdGuage)
	sname += '_' + afmt + '_' + str(af) + '_' + as1mt + '_' + str(as1)
	if as2 > 0: sname += '_' + as2mt + '_' + str(as2)
	sname +=  '_' + bfmt + '_' + str(bf) + '_' + bs1mt + '_' +str(bs1)
	if bs2 > 0: sname += '_' + bs2mt + '_' + str(bs2)
	
	afma, as1ma, as2ma = getMas(afmt, af), getMas(as1mt, as1), getMas(as2mt, as2)
	bfma, bs1ma, bs2ma = getMas(bfmt, bf), getMas(bs1mt, bs1), getMas(bs2mt, bs2)
	
	front = max(as1, as2, bs1, bs2)
	
	active = 0
	a1pos = a2pos = b1pos = b2pos = 0
	a1wait = a2wait = b1wait = b2wait = 0
	a1price = a2price = b1price = b2price = 0
	t = Trader(sname)
	for i in range(front, len(prices)):
		price = prices[i]
		
		volume = 0
		notes = ''
		oa1pos, oa2pos, ob1pos , ob2pos = a1pos, a2pos, b1pos , b2pos
		oa1wait, oa2wait, ob1wait, ob2wait = a1wait, a2wait, b1wait, b2wait
		
		std = np.std(ps[i-stdPeriod+1 : i+1], dtype=np.float64, ddof=0)
		if std >= stdGuage: active = 2
		else: active = 1
		if not checkTime(price['dt']): active = 0
		
		#A
		if as1 > 0 and afma[i - 1] <= as1ma[i - 1] and afma[i] > as1ma[i]:
			a1wait = 1
		
		if as1 > 0 and afma[i - 1] >= as1ma[i - 1] and afma[i] < as1ma[i]:
			a1wait = -1
		
		if as2 > 0 and afma[i - 1] <= as2ma[i - 1] and afma[i] > as2ma[i]:
			a2wait = 1
		
		if as2 > 0 and afma[i - 1] >= as2ma[i - 1] and afma[i] < as2ma[i]:
			a2wait = -1
		
		if active == 1: a1pos, a2pos = a1wait, a2wait
		if active != 0 and active != 1 and a1pos * a1wait == -1: a1pos = 0
		if active != 0 and active != 1 and a2pos * a2wait == -1: a2pos = 0
		
		if oa1pos != a1pos:
			volume += a1pos - oa1pos
			notes += 'A1:'+ str(oa1pos) + '->' + str(a1pos) + ';' + str(a1price) + '->' + str(price['rmb']) + ';'
			a1price = price['rmb']
			
		if oa2pos != a2pos:
			volume += a2pos - oa2pos
			notes += 'A2:'+ str(oa1pos) + '->' + str(a1pos) + ';' + str(a2price) + '->' + str(price['rmb']) + ';'
			a2price = price['rmb']
		
		#B
		if bs1 > 0 and bfma[i - 1] <= bs1ma[i - 1] and bfma[i] > bs1ma[i]:
			b1wait = 1
		
		if bs1 > 0 and bfma[i - 1] >= bs1ma[i - 1] and bfma[i] < bs1ma[i]:
			b1wait = -1
		
		if bs2 > 0 and bfma[i - 1] <= bs2ma[i - 1] and bfma[i] > bs2ma[i]:
			b2wait = 1
		
		if bs2 > 0 and bfma[i - 1] >= bs2ma[i - 1] and bfma[i] < bs2ma[i]:
			b2wait = -1
		
		if active == 2: b1pos, b2pos = b1wait, b2wait
		if active != 0 and active != 2 and b1pos * b1wait == -1: b1pos = 0
		if active != 0 and active != 2 and b2pos * b2wait == -1: b2pos = 0
		
		if ob1pos != b1pos:
			volume += b1pos - ob1pos
			notes += 'B1:'+ str(ob1pos) + '->' + str(b1pos) + ';' + str(b1price) + '->' + str(price['rmb']) + ';'
			b1price = price['rmb']
			
		if ob2pos != b2pos:
			volume += b2pos - ob2pos
			notes += 'B2:'+ str(ob2pos) + '->' + str(b2pos) + ';' + str(b2price) + '->' + str(price['rmb']) + ';'
			b2price = price['rmb']
		
		if volume != 0:
			t.processOrder(price['dt'], price['rmb'], volume, notes=notes)
		else:
			t.summary(price['dt'], price['rmb'])
		
	pool.estimate(t)
	return t
	
	
def getMas(matype, period):
	if matype == 'MA':
		return ma.calc_ma(ps, period)
	elif matype == 'EMA':
		return ma.calc_ema(ps, period)
	elif matype == 'SMA':
		return ma.calc_sma(ps, period)
	elif matype == 'LWMA':
		return ma.calc_lwma(ps, period)
	else:
		return None

def checkTime(dt):
	td = datetime.timedelta(hours=6)
	ndt = dt + td
	#return True
	#print ndt.weekday, ndt.hour
	if ndt.weekday() >= 5:
		return False
	
	if ndt.hour in [9, 10, 21, 22, 23, ]:
		return True
	
	if ndt.hour in [11, 15, ] and ndt.minute < 30:
		return True
	
	if ndt.hour in [13, ] and ndt.minute >= 30:
		return True
		
	return False
