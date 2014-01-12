# -*- coding: utf-8 -*-
from utils.db import SqliteDB
from utils.rwlogging import log
from indicator import ma

def calc_macd(prices, fast = 12, slow = 26, sign = 9):
	ps = [p['close'] for p in prices]
	macds = {}
	macds['fast'] = ma.calc_ema(ps, fast)
	macds['slow'] = ma.calc_ema(ps, slow)
	macds['dif'] = map(lambda f,s: round(f - s, 5), macds['fast'], macds['slow'])
	macds['sign'] = ma.calc_ma(macds['dif'], sign)
	
	return macds

def calc_all_macd(table, fast = 12, slow = 26, sign = 9):
	log.info('MACD generating for ' + table)
	
	db = SqliteDB().createIndicator(table, 'MACD', 'A', fast, slow, sign)
	prices = SqliteDB().getAllPrices(table)
	macds = calc_macd(prices, fast, slow, sign)
	
	for i in range(len(prices)):
		db.addIndicate(prices[i]['dtlong'], macds['sign'][i], macds['fast'][i], macds['slow'][i], macds['dif'][i])
	db.commit()
		
	log.info('MACD done')






