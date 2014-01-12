# -*- coding: utf-8 -*-
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from indicator import ma

def calc_kd(prices, kPeriod = 5, dPeriod = 3, slowing =3):
	phighs = [p['high'] for p in prices]
	plows = [p['low'] for p in prices]
	ps = [p['close'] for p in prices]
	l = len(prices)
	highest = [0] * l
	lowest = [0] * l
	kds = {}
	kds['k'] = [0] * l
	for i in range(kPeriod - 1, l):
		highest[i] = max(phighs[i-kPeriod+1 : i+1])
		lowest[i] = min(plows[i-kPeriod+1 : i+1])
		if i >= kPeriod + slowing - 1:
			highsum, lowsum = 0, 0
			for j in range(i - slowing + 1, i + 1):
				highsum += highest[j] - lowest[j]
				lowsum += ps[j] - lowest[j]
			#print i, highest[i], lowest[i], prices[j], highsum, lowsum
			#print i, highsum
			if highsum != 0:
				kds['k'][i] = round(lowsum / highsum * 100, 5)
				#print i, kds['k'][i]
	#print kds['k']
	kds['d'] = ma.calc_ma(kds['k'], dPeriod)
	
	return kds
	
def calc_all_kdj(table, kPeriod = 5, dPeriod = 3, slowing =3):
	log.info('KDJ generating for ' + table)
	
	db = SqliteDB().createIndicator(table, 'KDJ', 'A', kPeriod, dPeriod, slowing)
	prices = SqliteDB().getAllPrices(table)
	
	kds = calc_kd(prices, kPeriod, dPeriod, slowing)
	
	for i in range(len(prices)):
		db.addIndicate(prices[i]['dtlong'], kds['k'][i], kds['d'][i])
		
	log.info('KDJ done')
		
