# -*- coding: utf-8 -*-
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from indicator import ma


def calc_single_rsi(ps, period, preup, predown):
	l = len(ps)
	if l < period: return 0, 0, 0
	
	up = 0
	down = 0
	if l == period:
		deltas = np.diff(ps)
		for delta in deltas:
			if delta > 0: up = up + delta
			if delta < 0: down = down - delta
		if down == 0:
			rsi = 0
		else:
			rsi = round(100.0 - 100.0 / (up / down + 1.0), 5)
			up = round(up / period, 7)
			down = round(down / period, 7)
	else:
		delta = ps[-1] - ps[-2]
		if delta > 0: up = delta
		if delta < 0: down = 0 - delta
		
		up = round(up + preup * (period - 1) / period, 7)
		down = round(down + predown * (period - 1) / period, 7)
		if down == 0:
			rsi = 0
		else:
			rsi = round(100.0 - 100.0 / (up / down + 1.0), 5)
		
	return rsi, up , down

def calc_rsi(prices, period = 14):
	ps = [p['close'] for p in prices]
	rsis = {}
	rsis['rsi'] = []
	rsis['up'] = []
	rsis['down'] = []
	rsi, up, down, preup, predown = 0, 0, 0, 0, 0
	for i in range(len(ps)):
		rsi, up , down = calc_single_rsi(ps[:i+1], period, preup, predown)
		rsis['rsi'].append(rsi)
		rsis['up'].append(up)
		rsis['down'].append(down)
		preup, predown = up , down
		
	return rsis
	
def calc_all_rsi(table, period = 14):
	log.info('RSI generating for ' + table)
	
	db = SqliteDB().createIndicator(table, 'RSI', 'A', period)
	prices = SqliteDB().getAllPrices(table)
	rsis = calc_rsi(prices, period)
	
	for i in range(len(prices)):
		db.addIndicate(prices[i]['dtlong'], rsis['rsi'][i], rsis['up'][i], rsis['down'][i])
	
	log.info('RSI done')
	