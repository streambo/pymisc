# -*- coding: utf-8 -*-
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log


def calc_ma(datas, period):
	mas = []
	for i in range(len(datas)):
		if i < period - 1:
			ma = 0
		else:
			r = np.mean(datas[i-period+1 : i+1])
			ma = round(r, 5)
			
		mas.append(ma)
		prema = ma

	return mas		
	
def calc_ema(datas, period):
	prema = 0
	mas = []
	for i in range(len(datas)):
		if i == 0:
			ma = datas[0]
		else:
			r = (datas[i] * 2 + prema * (period - 1)) / (period + 1)
			ma = round(r, 5)
			
		mas.append(ma)
		prema = ma

	return mas
	
def calc_sma(datas, period):
	prema = 0
	mas = []
	for i in range(len(datas)):
		if i < period - 1:
			ma = 0
		elif i == period - 1:
			ma = np.mean(datas[:i+1])
		else:
			r = (datas[i] + prema * (period - 1)) / period
			ma = round(r, 5)
			
		mas.append(ma)
		prema = ma
	return mas
	
def calc_lwma(datas, period):
	l = len(datas)
	mas = [0] * l
	if l < period: return mas
	
	sum, lsum, weight = 0, 0, 0
	
	for i in range(period):
		sum += datas[i] * (i + 1)
		lsum += datas[i]
		weight += i + 1
		
	for i in range(period - 1, l):
		mas[i] = round(sum / weight, 5)
		if i == l - 1: break
		sum = sum - lsum + datas[i+1] * period
		lsum = lsum - datas[i-period+1] + datas[i+1]
		
	return mas

def calc_dynamic_ma(datas, weight):
	l = len(datas)
	mas = [0] * l
	
	if l < 2:
		return mas
	
	mas[0] = datas[0]
	for i in range(1, l):
		mas[i] = round(datas[i] * weight + mas[i-1] * (1 - weight), 5)
		
	return mas[i]

def calc_all_ma(table, matype, period, weight = 0):
	log.info('MA generating ' + matype + ' for ' + table)
	
	db = SqliteDB().createIndicator(table, 'MA', matype, period, weight)
	prices = SqliteDB().getAllPrices(table)
	ps = [p['close'] for p in prices]
	
	if matype == 'MA':
		mas = calc_ma(ps, period)
	elif matype == 'EMA':
		mas = calc_ema(ps, period)
	elif matype == 'SMA':
		mas = calc_sma(ps, period)
	elif matype == 'LWMA':
		mas = calc_lwma(ps, period)

	for i in range(len(prices)):
		db.addIndicate(prices[i]['dtlong'], mas[i])
	db.commit()
		
	log.info('MA done')
	return mas
		