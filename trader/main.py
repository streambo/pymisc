# -*- coding: utf-8 -*-
import datetime, time, csv, os
from utils.db import SqliteDB
from utils.rwlogging import log
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj

path = os.path.dirname(__file__)

def strategyMA():
	table = 'XAGUSD1440'
	prices = SqliteDB().getAllPrices(table)
	ps = [p[6] for p in prices]
	ma5 = ma.calc_ma(ps, 5)
	ma10 = ma.calc_ma(ps, 10)
	ma20 = ma.calc_ma(ps, 20)
	
	t = Trader()
	for i in range(20, len(prices)):
		if ma5[i - 1] < ma10[i - 1] and ma5[i] >= ma10[i]:
			t.buy(prices[i][1], prices[i][2], prices[i][8])
			
		if ma5[i - 1] < ma20[i - 1] and ma5[i] >= ma20[i]:
			t.buy(prices[i][1], prices[i][2], prices[i][8])
			
		if ma5[i - 1] > ma10[i - 1] and ma5[i] <= ma10[i]:
			t.sell(prices[i][1], prices[i][2], prices[i][8])
		
		t.show(prices[i][1], prices[i][2], prices[i][8])
	t.generateGraph()
			
def strategyBolling():
	table = 'XAGUSD1440'
	prices = SqliteDB().getAllPrices(table)
	ps = [p[6] for p in prices]
	bollings = bolling.calc_bolling(ps, 20, 2)
	
	t = Trader()
	for i in range(20, len(prices)):
		if bollings['boll'][i] >= -2 and bollings['boll'][i-1] < -2 and t.position >= 0:
			t.sell(prices[i][1], prices[i][2], prices[i][8])
		
		if bollings['boll'][i] >= 2 and bollings['boll'][i-1] < 2 and t.position <= 0:
			t.buy(prices[i][1], prices[i][2], prices[i][8])
			
		t.show(prices[i][1], prices[i][2], prices[i][8])
		
	t.generateGraph()
	
def calculateIndicators():
	#tables = ['XAGUSD30', 'XAGUSD60', 'XAGUSD240', 'XAGUSD1440', 'XAGUSD10080', 'XAGUSD43200', ]
	#for table in tables:
	h1ma5 = ma.calc_all_ma('XAGUSD1440', 'LWMA', 5)
	return
	bollings = bolling.calc_all_bolling('XAGUSD1440')
	macds = macd.calc_all_macd('XAGUSD1440')
	rsis = rsi.calc_all_rsi('XAGUSD1440')
	kdjs = kdj.calc_all_kdj('XAGUSD1440')
	#return
	h1ma5 = ma.calc_all_ma('XAGUSD1440', 'MA', 5)
	h1ma10 = ma.calc_all_ma('XAGUSD1440', 'MA', 10)
	h1ma20 = ma.calc_all_ma('XAGUSD1440', 'MA', 20)
	h1ema5 = ma.calc_all_ma('XAGUSD1440', 'EMA', 5)
	h1ema10 = ma.calc_all_ma('XAGUSD1440', 'EMA', 10)
	h1ema20 = ma.calc_all_ma('XAGUSD1440', 'EMA', 20)
	#return
	h1sma5 = ma.calc_all_ma('XAGUSD1440', 'SMA', 5)
	h1sma10 = ma.calc_all_ma('XAGUSD1440', 'SMA', 10)
	h1sma20 = ma.calc_all_ma('XAGUSD1440', 'SMA', 20)
	
	

def importAll():
	#tables = ['XAGUSD1', 'XAGUSD5', 'XAGUSD15', 'XAGUSD30', 'XAGUSD60', 'XAGUSD240', 'XAGUSD1440', 'XAGUSD10080', 'XAGUSD43200', ]
	tables = ['XAGUSD1440',]
	for table in tables:
		log.info('importing ' + table)
		importTable(table)
		log.info('done ' + table)
	
def importTable(table):
	db = SqliteDB()
	prec = 0
	with open(os.path.join(path, 'data/' + table + '.csv'), 'rb') as csvfile:
		rdr = csv.reader(csvfile)
		for row in rdr:
			p = {}
			p['open'] = float(row[2])
			p['high'] = float(row[3])
			p['low'] = float(row[4])
			p['close'] = float(row[5])
			p['vol'] = float(row[6])
			p['rmb'] = round(p['close'] * 6.1 / 31.1035, 3)
			p['dt'] = datetime.datetime.strptime(row[0] + ' ' + row[1], '%Y.%m.%d %H:%M') #2009.06.01,00:00
			p['dtlong'] = time.mktime(p['dt'].timetuple())
			p['date'] = p['dt'].strftime('%Y-%m-%d')
			p['time'] = p['dt'].strftime('%H:%M:%S')
			p['chan'] = p['close'] - prec
			if prec == 0:
				p['per'] = 0
			else:
				p['per'] = round((p['close'] - prec) * 100 / prec, 3)
			prec = p['close']
			db.addData(table, (p['dtlong'], p['date'], p['time'], p['open'], p['high'], p['low'], p['close'],
p['vol'], p['rmb'], p['chan'], p['per'], ))


if __name__ == "__main__":
	importAll()
	calculateIndicators()
	#strategyMA()
	#strategyBolling()



