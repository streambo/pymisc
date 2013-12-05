# -*- coding: utf-8 -*-
import os
import sqlite3
from rwlogging import log

class SqliteDB():
	def __init__(self):
		self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'sqlite.db').replace('\\','/'), timeout=10)
		self.initTables()
	def initTables(self):
		cur = self.conn.cursor()
		cur.execute('''
CREATE TABLE IF NOT EXISTS FEDATA
(SEQNO  INTEGER PRIMARY KEY NOT NULL,
DTYPE  TEXT,
DTLONG INTEGER,
DDATE  TEXT,
DTIME  TEXT,
DVALUE REAL,
NOTES  TEXT,
FETCHDT INTEGER,
FETCHDATE TEXT,
FETCHTIME TEXT
)
''')
		cur.execute('''
CREATE TABLE IF NOT EXISTS NOTICE
(SEQNO   INTEGER PRIMARY KEY NOT NULL,
DTYPE    TEXT,
DSUBTYPE INTEGER,
DTLONG   INTEGER,
DDATE    TEXT,
DTIME    TEXT,
DVALUE   REAL,
DPERCENT REAL,
DTEXT    TEXT,
NOTES    TEXT
)
''')
		cur.close()
	def dropTables(self):
		cur = self.conn.cursor()
		cur.execute('DROP TABLE IF EXISTS FEDATA')
		cur.execute('DROP TABLE IF EXISTS NOTICE')
		self.conn.commit()
	def emptyTables(self):
		cur = self.conn.cursor()
		cur.execute('DELETE FROM FEDATA')
		cur.execute('DELETE FROM NOTICE')
		self.conn.commit()
	
	def addPrice(self, data):
		cur = self.conn.cursor()
		cur.execute('SELECT DTLONG FROM FEDATA WHERE DTYPE=? AND DTLONG=?', (data[0], long(data[1]),))
		if cur.fetchone() == None:
			log.debug('inserting price: ' + data[0] + ' ' + str(data[1]) + ' ' + data[3] + ' ' + str(data[4]))
			cur.execute('INSERT INTO FEDATA(DTYPE,DTLONG,DDATE,DTIME,DVALUE,NOTES,FETCHDT,FETCHDATE,FETCHTIME) VALUES(?,?,?,?,?,?,?,?,?)', data)
		self.conn.commit()
		cur.close()
		return
		
	def getPrice(self, ptype, qtime):
		cur = self.conn.cursor()
		#print cur.execute('select * from FEDATA').fetchall()
		cur.execute('SELECT DVALUE FROM FEDATA WHERE DTYPE=? AND DTLONG<=? ORDER BY DTLONG', (ptype, qtime))
		val = cur.fetchone()
		if val:
			return val[0]
		else:
			return None
		
	def addNotice(self, data):
		cur = self.conn.cursor()
		log.debug('inserting notice: ' + str(data[0]) + ',' + str(data[1]) + ',' + str(data[4]) + ',' + str(data[6]))
		cur.execute('INSERT INTO NOTICE(DTYPE,DSUBTYPE,DTLONG,DDATE,DTIME,DVALUE,DPERCENT,DTEXT,NOTES) VALUES(?,?,?,?,?,?,?,?,?)', data)
		self.conn.commit()
		cur.close()
		return
		
	def updateNotice(self, data):
		cur = self.conn.cursor()
		#print cur.execute('select * from NOTICE').fetchall()
		cur.execute('SELECT DTLONG FROM NOTICE WHERE DTYPE=? AND DSUBTYPE=? AND DDATE=?', (data[0], data[1], data[3],))
		if cur.fetchone() == None:
			log.debug('inserting notice: ' + str(data[0]) + ',' + str(data[1]) + ',' + str(data[4]) + ',' + str(data[6]))
			cur.execute('INSERT INTO NOTICE(DTYPE,DSUBTYPE,DTLONG,DDATE,DTIME,DVALUE,DPERCENT,DTEXT,NOTES) VALUES(?,?,?,?,?,?,?,?,?)', data)
		else:
			log.debug('updating notice: ' + str(data[0]) + ',' + str(data[1]) + ',' + str(data[4]) + ',' + str(data[6]))
			cur.execute('UPDATE NOTICE SET DTLONG=?,DTIME=?,DVALUE=?,DPERCENT=?,DTEXT=? WHERE DTYPE=? AND DSUBTYPE=? AND DDATE=?', (data[2], data[4], data[5], data[6], data[7],data[0], data[1], data[3]))
		self.conn.commit()
		cur.close()
		return
		
	def getNotice(self, ptype, psubtype, qdate):
		cur = self.conn.cursor()
		cur.execute('SELECT DPERCENT FROM NOTICE WHERE DTYPE=? AND DSUBTYPE=? AND DDATE<=?', (ptype, psubtype, qdate))
		val = cur.fetchone()
		if val:
			return val[0]
		else:
			return 0
		
	def getNoticeCount(self, ptype, psubtype, qtime):
		cur = self.conn.cursor()
		cur.execute('SELECT COUNT(*) FROM NOTICE WHERE DTYPE=? AND DSUBTYPE=? AND DTLONG>=? ORDER BY DTLONG', (ptype, psubtype, qtime))
		return cur.fetchone()[0]


