# -*- coding: utf-8 -*-
import datetime, time, csv, os, shutil
from utils.db import SqliteDB
from utils.rwlogging import log
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy import maTrader

path = os.path.dirname(__file__)

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
	
def calculateIndicators(table):
	#tables = ['XAGUSD30', 'XAGUSD60', 'XAGUSD240', 'XAGUSD1440', 'XAGUSD10080', 'XAGUSD43200', ]
	#for table in tables:
	h1ma5 = ma.calc_all_ma(table, 'LWMA', 5)
	#return
	bollings = bolling.calc_all_bolling(table)
	macds = macd.calc_all_macd(table)
	rsis = rsi.calc_all_rsi(table)
	kdjs = kdj.calc_all_kdj(table)
	#return
	h1ma5 = ma.calc_all_ma(table, 'MA', 5)
	h1ma10 = ma.calc_all_ma(table, 'MA', 10)
	h1ma20 = ma.calc_all_ma(table, 'MA', 20)
	h1ema5 = ma.calc_all_ma(table, 'EMA', 5)
	h1ema10 = ma.calc_all_ma(table, 'EMA', 10)
	h1ema20 = ma.calc_all_ma(table, 'EMA', 20)
	#return
	h1sma5 = ma.calc_all_ma(table, 'SMA', 5)
	h1sma10 = ma.calc_all_ma(table, 'SMA', 10)
	h1sma20 = ma.calc_all_ma(table, 'SMA', 20)
	
	

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
	db.commit()

def clearLog():
	logdir = os.path.join(path, 'logs')
	rsdir = os.path.join(path, 'result')
	shutil.rmtree(rsdir)
	os.mkdir(rsdir)
	
	logfiles =['trader.csv' ,'balance.csv' ,'trades.csv' ,'strategy.csv' ,]
	for logfile in logfiles:
		with open(os.path.join(logdir, logfile), 'w'):
			pass
	#print logdir, lsdir
	#shutil.rmtree(logdir)
	#os.mkdir(logdir)
	
if __name__ == "__main__":
	clearLog()
	#importAll()
	#importTable('XAGUSD1440')
	maTrader.runStrategy('XAGUSD1440')
	#calculateIndicators('XAGUSD1440')
	#strategyMA()
	#strategyBolling()



