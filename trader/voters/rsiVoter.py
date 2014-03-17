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
	log.debug('beginning rsi voter ...')
	
	starttime = time.time() 
	pool = VoterPool(5, prices)
	
	#calcTickets(pool, 12, 26, 9)
	#calcTickets(pool, 'SMA', 3, 'EMA', 4)
	#calcTickets(pool, 'MA', 7, 'SMA', 13)
	#pool.showVoters()
	#return
	
	for i in range(5, 50):
		calcTickets(pool, prices, i)
		
	pool.showVoters()
	
def calcTickets(pool, prices, period):
	vname = 'RSI_' + str(period)
	rsis = rsi.calc_rsi(prices, period)
	front = period
	l = len(prices)
	ops = [0] * l
	for i in range(front, l):
		if rsis['rsi'][i] < 30 and rsis['rsi'][i] > rsis['rsi'][i-1]:
			ops[i] = 1
		elif ops[i-1] == 1 and rsis['rsi'][i] > rsis['rsi'][i-1]:
			ops[i] = 1
		elif rsis['rsi'][i] > 70 and rsis['rsi'][i] < rsis['rsi'][i-1]:
			ops[i] = -1
		elif ops[i-1] == -1 and rsis['rsi'][i] < rsis['rsi'][i-1]:
			ops[i] = -1
	
	pool.estimate(vname, ops, front)
		
	