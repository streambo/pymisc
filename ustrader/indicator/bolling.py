# -*- coding: utf-8 -*-
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from indicator import ma

def calc_boll(ps, period, deviate):
	l = len(ps)
	if l < period: return 0, 0, 0, 0, 0
	
	mean = np.mean(ps[-period:])
	std = round(np.std(ps[-period:], dtype=np.float64), 5)
	if std == 0:
		boll = 0
	else:
		boll = round((ps[-1] - mean) / std, 5)
	bupper = mean + deviate * std
	blower = mean - deviate * std
	return (mean, std, boll, bupper, blower)

def calc_bolling(prices, period = 20, deviate = 2):
	ps = [p['close'] for p in prices]
	bs = [calc_boll(ps[:i+1], period, deviate) for i in range(len(ps))]
	bollings = {}
	bollings['mean'], bollings['std'], bollings['boll'], bollings['upper'], bollings['lower'] = zip(*bs)
	bollings['mean'] = list(bollings['mean'])
	bollings['std'] = list(bollings['std'])
	bollings['boll'] = list(bollings['boll'])
	bollings['upper'] = list(bollings['upper'])
	bollings['lower'] = list(bollings['lower'])
	
	return bollings
	
def calc_all_bolling(table, period = 20, deviate = 2):
	log.info('Bolling generating for ' + table)
	
	db = SqliteDB().createIndicator(table, 'BOLLING', 'A', period, deviate)
	prices = SqliteDB().getAllPrices(table)
	bollings = calc_bolling(prices, period, deviate)
	
	for i in range(len(prices)):
		db.addIndicate(prices[i]['dtlong'], bollings['boll'][i], bollings['mean'][i], bollings['upper'][i], bollings['lower'][i], bollings['std'][i])
		
	db.commit()
	log.info('Bolling done')
		
		