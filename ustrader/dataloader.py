# -*- coding: utf-8 -*-
import datetime, time, csv, os, shutil
from utils.db import SqliteDB
from utils.rwlogging import log

path = os.path.dirname(__file__)

def importAll():
	#tables = ['XAGUSD1', 'XAGUSD5', 'XAGUSD15', 'XAGUSD30', 'XAGUSD60', 'XAGUSD240', 'XAGUSD1440', 'XAGUSD10080', 'XAGUSD43200', ]
	tables = ['XAGUSD1440',]
	for table in tables:
		log.info('importing ' + table)
		importTable(table)
		log.info('done ' + table)
	
def importToArray(table):
	log.debug('loading ' + table + ' ...')
	prices = []
	prec = 0
	with open(os.path.join(path, '../trader_data/' + table + '.csv'), 'rb') as csvfile:
		rdr = csv.reader(csvfile)
		for row in rdr:
			p = {}
			p['open'] = float(row[2])
			p['high'] = float(row[3])
			p['low'] = float(row[4])
			p['close'] = float(row[5])
			p['vol'] = float(row[6])
			p['rmb'] = round(p['close'] * 6.1 * 10 / 31.1035, 2)
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
			prices.append(p)
	return prices
		
def importTable(table):
	db = SqliteDB()
	prices = importToArray(table)
	for p in prices:
		db.addData(table, (p['dtlong'], p['date'], p['time'], p['open'], p['high'], p['low'], p['close'],
p['vol'], p['rmb'], p['chan'], p['per'], ))
	
	db.commit()
