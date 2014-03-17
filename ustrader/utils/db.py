# -*- coding: utf-8 -*-
import os, time
import sqlite3
from utils.rwlogging import log

class SqliteDB():
	def __init__(self):
		self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'sqlite.db').replace('\\','/')
,timeout=10, check_same_thread=False)
		self.conn.row_factory = sqlite3.Row
		self.initTables()
	def emptyTables(self):
		cur = self.conn.cursor()
		cur.execute('DELETE FROM XAGUSD1440')
		self.conn.commit()
		log.debug('Emptied')
		
	def commit(self):
		self.conn.commit()
		
	def addData(self, table, data):
		cur = self.conn.cursor()
		cur.execute('SELECT DTLONG FROM ' + table + ' WHERE DTLONG=?', (long(data[0]),))
		if cur.fetchone() == None:
			#log.debug('inserting ' + table + ' : ')
			#log.info(data)
			#cur.execute('INSERT INTO PRICE(DTLONG,DDATE,DTIME,DCLOSE,DHIGH,DLOW,DOPEN,DRMB,DVOL,DINX1,DINX2,DINX3,DINX4,DINX5,DINX6,DNOTES) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)
			cur.execute('INSERT INTO ' + table + ' VALUES(?,?,?,?,?,?,?,?,?,?,?)', data)
		else:
			log.info('** data duplicate ** ' + table + ' : ')
			log.info(data)
		cur.close()
		return
		
	def getAllPrices(self, table):
		cur = self.conn.cursor()
		cur.execute('''SELECT 
DTLONG as dtlong, DDATE as date, DTIME as time, DOPEN as open, 
DHIGH as high, DLOW as low, DCLOSE as close, DVOL as vol, 
DRMB as rmb, DCHAN as chan, DPERC as per FROM ''' + table + ' ORDER BY DTLONG')
		return cur.fetchall()
	
	def createIndicator(self, dtype, itype, subtype, arg1 = 0, arg2 = 0, arg3 = 0, arg4 = 0, arg5 = 0):
		self.table = dtype + '_' + itype + '_' + subtype + '_' + str(arg1) + '_' + str(arg2) + '_' + str(arg3) + '_' + str(arg4) + '_' + str(arg5)
		log.info('create table ' + self.table)
		cur = self.conn.cursor()
		cur.execute('''
CREATE TABLE IF NOT EXISTS ''' + self.table + '''
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
VAL1   REAL,
VAL2   REAL,
VAL3   REAL,
VAL4   REAL,
VAL5   REAL,
VAL6   REAL,
VAL7   REAL,
VAL8   REAL
)
''')
		cur.execute('DELETE FROM ' + self.table)
		self.conn.commit()
		cur.close()
		return self
		
	def addIndicate(self, dtlong, val1, val2 = 0, val3 = 0, val4 = 0, val5 = 0, val6 = 0, val7 = 0, val8 = 0):
		cur = self.conn.cursor()
		cur.execute('SELECT DTLONG FROM ' + self.table + ' WHERE DTLONG=?', (dtlong,))
		if cur.fetchone() == None:
			dt = time.localtime(dtlong)
			ddate = time.strftime('%Y-%m-%d', dt)
			dtime = time.strftime('%H:%M:%S', dt)
			#log.debug('inserting ' + self.table + ' : ' + str(val1))
			#log.info(data)
			cur.execute('INSERT INTO ' + self.table + ' VALUES(?,?,?,?,?,?,?,?,?,?,?)', (dtlong,ddate,dtime,val1,val2,val3,val4,val5,val6,val7,val8))
		else:
			log.info('** data duplicate ** ' + self.table + ' : ')
			log.info(data)
		#self.conn.commit()
		cur.close()
		return
		
		
	def getPrice(self, ptype, qtime):
		cur = self.conn.cursor()
		#print cur.execute('select * from FEDATA').fetchall()
		cur.execute('SELECT DVALUE,DPER,DOPEN,DTIME FROM FEDATA WHERE DTYPE=? AND DTLONG<=? ORDER BY DTLONG DESC', (ptype, qtime))
		val = cur.fetchone()
		if val:
			return val
		else:
			return None
		

	def initTables(self):
		cur = self.conn.cursor()
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD1
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD5
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD15
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD30
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD60
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD240
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD1440
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD10080
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS XAGUSD43200
(
DTLONG INTEGER PRIMARY KEY,
DDATE  TEXT,
DTIME  TEXT,
DOPEN  REAL,
DHIGH  REAL,
DLOW   REAL,
DCLOSE REAL,
DVOL   REAL,
DRMB   REAL,
DCHAN  REAL,
DPERC  REAL
)
''')
		cur.close()