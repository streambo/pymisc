# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
import matplotlib.pyplot as plt
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import balLogger as logb
from utils.rwlogging import tradesLogger as logtr
from indicator import ma, macd, bolling, rsi, kdj
#from voters.pool import VoterPool
from voters import pool
from strader import Trader

prices = areas = l = None
COUNT_DOWN = 24

def runVoter(in_prices):
	global prices, areas, l
	prices = in_prices
	directs, slopes, stds, areas = pool.calc_variants(prices)
	l = len(prices)
	ps = [p['close'] for p in prices]
	
	mafront, maOps = getMaOps(ps)
	doTrade('MA', mafront, maOps)
	return
	
def getMaOps(ps):
	ops = [0, 0, 0, 0]
	ops[0] = genMaOps(ps, 'MA', 29, 'SMA', 90)
	ops[1] = genMaOps(ps, 'SMA', 23, 'EMA', 45)
	ops[2] = genMaOps(ps, 'SMA', 23, 'EMA', 45)
	ops[3] = genMaOps(ps, 'SMA', 8, 'EMA', 10)
	front = 85
	
	fops = [0] * l
	for i in range(l):
		fops[i] = ops[areas[i]][i]
		#if areas[i] == 0: fops[i] = 0
		#if areas[i] == 1: fops[i] = 0
		#if areas[i] == 2: fops[i] = 0
	return front, fops
		
def doTrade(tname, front, ops):
	
	pools = pool.VoterPool(1, prices)
	pools.estimate(tname, ops, front)
	pools.showVoters()
	
	t = Trader(tname)
	lastArea = -1
	countdowns = [COUNT_DOWN] * 4
	vols = [0] * 4
	for i in range(front, l):
		price = prices[i]
		volume = 0
		area = areas[i]
		if pool.checkTime(price['dt']):
			if vols[area] == 0:
				notes = 'AREA:' + str(area) + ';VOL:' + str(vols[area]) + '->' + str(ops[i]) + ';'
				volume = ops[i] - vols[area]
				vols[area] = ops[i]
				countdowns[area] = COUNT_DOWN
			
			if volume == 0: notes = ''
			for j in range(4):
				#if j == area: continue
				if countdowns[j] > 0: countdowns[j] -= 1
				if countdowns[j] == 0 and vols[j] != 0:
					volume -= vols[j]
					notes += 'CLOSE AREA:' + str(j) + ';VOL:' + str(vols[j]) + '->0;'
					vols[j] = 0
		else: # not trading time
			for j in range(4):
				if countdowns[j] > 0: countdowns[j] -= 1
		
		if volume != 0:
			t.processOrder(price['dt'], price['rmb'], volume, notes=notes)
		else:
			t.summary(price['dt'], price['rmb'])
	
	logs.info(t.strategyName + ',' + str(len(t.stats['buy']['date'])) + ',' + str(len(t.stats['sell']['date'])) + ',' + str(t.stats['downDays']) + ',' + str(t.equity))
	logtr.info('OP,STRATEGY,TIME,VOLUME,PRICE,POSITION,NOTES,EQUITY,BALANCE')
	for tl in t.stats['log']:
		logtr.info(tl)
	t.generateGraph(0)
	
	
def genMaOps(ps, ft, f, st, s):
	
	if ft == 'MA':
		fma = ma.calc_ma(ps, f)
	elif ft == 'EMA':
		fma = ma.calc_ema(ps, f)
	elif ft == 'SMA':
		fma = ma.calc_sma(ps, f)
	elif ft == 'LWMA':
		fma = ma.calc_lwma(ps, f)
		
	if st == 'MA':
		sma = ma.calc_ma(ps, s)
	elif st == 'EMA':
		sma = ma.calc_ema(ps, s)
	elif st == 'SMA':
		sma = ma.calc_sma(ps, s)
	elif st == 'LWMA':
		sma = ma.calc_lwma(ps, s)
		
	
	l = len(ps)
	ops = [0] * l
	for i in range(s, l):
		diff = fma[i] - sma[i]
		if diff > 0:
			ops[i] = 1
		elif diff < 0:
			ops[i] = -1
			
	return ops
	
	
	

def runVoter_0(in_prices):
	global prices, areas, l
	prices = in_prices
	directs, slopes, stds, areas = pool.calc_variants(prices)
	l = len(prices)
	ps = [p['close'] for p in prices]
	
	mafront, maOps = getMaOps(ps)
	doTrade('MA', mafront, maOps)
	return
	
	macdfront, macdOps = getMacdOps(prices)
	doTrade('MACD', macdfront, macdOps)
	return
	
	front = max(mafront, macdfront)
	ops = [0] * l
	for i in range(l):
		if maOps[i] + macdOps[i] >= 2:
			ops[i] = 1
		elif maOps[i] + macdOps[i] <= -2:
			ops[i] = -1
			
	doTrade('MA', front, ops)
	return
	
def getMacdOps(prices):
	ops = [0, 0, 0, 0]
	ops[0] = genMacdOps(prices, 2, 9, 11)
	ops[1] = genMacdOps(prices, 2, 6, 2)
	ops[2] = genMacdOps(prices, 21, 56, 3)
	ops[3] = genMacdOps(prices, 6, 11, 17)
	front = 63
	
	fops = [0] * l
	for i in range(l):
		fops[i] = ops[areas[i]][i]
	return front, fops

def genMacdOps2(prices, fast, slow, sign):
	openLevel, closeLevel = 0.2, 0.1
	macds = macd.calc_macd(prices, fast, slow, sign)
	front = slow + sign
	
	l = len(prices)
	ops = [0] * l
	for i in range(front, l):
		if macds['macd'][i] < 0 and macds['macd'][i] > macds['sign'][i] and abs(macds['macd'][i]) > openLevel:
			ops[i] = 1
		elif ops[i-1] == -1 and macds['macd'][i] < 0 and macds['macd'][i] > macds['sign'][i] and abs(macds['macd'][i]) > closeLevel:
			ops[i] = 0
		elif macds['macd'][i] > 0 and macds['macd'][i] < macds['sign'][i] and abs(macds['macd'][i]) > openLevel:
			ops[i] = -1
		elif ops[i-1] == 1 and macds['macd'][i] > 0 and macds['macd'][i] < macds['sign'][i] and abs(macds['macd'][i]) > closeLevel:
			ops[i] = 0
		else:
			ops[i] = ops[i-1]
	return ops
	
def genMacdOps(prices, fast, slow, sign):
	openLevel, closeLevel = 0.2, 0.1
	macds = macd.calc_macd(prices, fast, slow, sign)
	front = slow + sign
	
	l = len(prices)
	ops = [0] * l
	for i in range(front, l):
		if macds['sign'][i] > 0.1 and macds['macd'][i] > macds['sign'][i]:
			ops[i] = 1
		elif macds['macd'][i] > 0.1 and macds['macd'][i] < macds['sign'][i]:
			ops[i] = -1
		if macds['sign'][i] < -0.1 and macds['macd'][i] < macds['sign'][i]:
			ops[i] = -1
		elif macds['macd'][i] < -0.1 and macds['macd'][i] > macds['sign'][i]:
			ops[i] = 1
			
	return ops
	