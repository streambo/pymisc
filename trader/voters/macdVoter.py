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

openLevel, closeLevel = 0.2, 0.1
	
def runVoter(prices):
	log.debug('beginning macd voter ...')
	
	log.debug('running ma voter ...')
	starttime = time.time() 
	pool = VoterPool(5, prices)
	
	
	#calcTickets(pool, 12, 26, 9)
	#calcTickets(pool, 'SMA', 3, 'EMA', 4)
	#calcTickets(pool, 'MA', 7, 'SMA', 13)
	#pool.showVoters()
	#return
	
	for i in range(2, 30):
		for j in range(5, 60):
			if i > j: continue
			elapsed = long(time.time() - starttime)
			log.debug('== ' + str(elapsed) + ',' + str(i) + '_' + str(j) + ' ==')
			for k in range(2, 30):
				calcTickets(pool, prices, i, j, k)
	
	pool.showVoters()
			
def calcTickets2(pool, prices, fast, slow, sign):
	vname = 'MACD_' + str(fast) + '_' + str(slow) + '_' + str(sign)
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
	
	pool.estimate(vname, ops, front)
	
def calcTickets(pool, prices, fast, slow, sign):
	vname = 'MACD_' + str(fast) + '_' + str(slow) + '_' + str(sign)
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
	
	pool.estimate(vname, ops, front)

		