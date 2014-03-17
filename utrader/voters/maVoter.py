# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
import matplotlib.pyplot as plt
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import balLogger as logb
from indicator import ma, macd, bolling, rsi, kdj
from voters.pool import VoterPool

mas = emas = smas = lwmas = prices = None
	
def runVoter(in_prices):
	global mas, emas, smas, lwmas, prices
	log.debug('beginning ma voter ...')
	
	prices = in_prices
	ps = [p['close'] for p in prices]
	
	mas = [0] * 61
	emas = [0] * 61
	smas = [0] * 61
	lwmas = [0] * 61
	for period in range(2, 61):
		mas[period] = ma.calc_ma(ps, period)
		emas[period] = ma.calc_ema(ps, period)
		smas[period] = ma.calc_sma(ps, period)
		lwmas[period] = ma.calc_lwma(ps, period)
	
	
	log.debug('running ma voter ...')
	starttime = time.time() 
	matypes = ['MA', 'EMA', 'SMA', 'LWMA']
	
	pool = VoterPool(2, prices)
	#calcTickets(pool, 'MA', 7, 'EMA', 18)
	#calcTickets(pool, 'SMA', 3, 'EMA', 4)
	#calcTickets(pool, 'MA', 7, 'SMA', 13)
	#pool.showVoters()
	#return
	
	
	farr = range(2, 10)
	sarr = range(4, 60)
	
	for ft, f in [(matype, period) for matype in matypes for period in farr]:
		elapsed = long(time.time() - starttime)
		#log.debug('== ' + str(elapsed) + ',' + ft + '_' + str(f) + ' ==')
		for st, s in [(matype, period) for matype in matypes for period in sarr]:
			if s < f: continue
			calcTickets(pool, ft, f, st, s)
	
	pool.showVoters()
			
def calcTickets(pool, ft, f, st, s):
	global prices
	
	vname = 'MA_' + ft + '_' + str(f) + '_' + st + '_' + str(s)
	front = s
	
	fma, sma = getMas(ft, f), getMas(st, s)
	
	l = len(prices)
	ops = [0] * l
	for i in range(s, l):
		diff = fma[i] - sma[i]
		if diff > 0:
			ops[i] = 1
		elif diff < 0:
			ops[i] = -1
	
	pool.estimate(vname, ops, front)

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
		