# coding=UTF-8
import os
import sqlite3

class FDatabase():
    def __init__(self):
        self.conn = sqlite3.connect('/mnt/sata/developments/db/fdata.db', timeout=10)
    def createTables(self):
        cur = self.conn.cursor()
        cur.execute('''
CREATE TABLE IF NOT EXISTS SILVERRMB
(SEQNO  INTEGER PRIMARY KEY NOT NULL,
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
CREATE TABLE IF NOT EXISTS GOLDUSD
(SEQNO  INTEGER PRIMARY KEY NOT NULL,
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
CREATE TABLE IF NOT EXISTS AGTD
(SEQNO  INTEGER PRIMARY KEY NOT NULL,
DTLONG INTEGER,
DDATE  TEXT,
DTIME  TEXT,
DVALUE REAL,
VOLUME INTEGER,
NOTES  TEXT,
FETCHDT INTEGER,
FETCHDATE TEXT,
FETCHTIME TEXT
)
''')
        cur.execute('''
CREATE TABLE IF NOT EXISTS USDX
(SEQNO  INTEGER PRIMARY KEY NOT NULL,
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
CREATE TABLE IF NOT EXISTS USADJI
(SEQNO  INTEGER PRIMARY KEY NOT NULL,
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
        cur.close()
    def dropTables(self):
        cur = self.conn.cursor()
        #cur.execute('DROP TABLE IF EXISTS SILVERRMB')
        #cur.execute('DROP TABLE IF EXISTS GOLDUSD')
        #cur.execute('DROP TABLE IF EXISTS AGTD')
        #cur.execute('DROP TABLE IF EXISTS USDX')
        cur.execute('DROP TABLE IF EXISTS USADJI')
        self.conn.commit()
    def emptyTables(self):
        cur = self.conn.cursor()
        #cur.execute('DELETE FROM SILVERRMB')
        #cur.execute('DELETE FROM GOLDUSD')
        #cur.execute('DELETE FROM AGTD')
        #cur.execute('DELETE FROM USDX')
        cur.execute('DELETE FROM USADJI')
        self.conn.commit()
    def addData(self, table, data):
        cur = self.conn.cursor()
        cur.execute('SELECT DTLONG FROM ' + table + ' WHERE DTLONG=?', (long(data[0]),))
        if cur.fetchone() == None:
            print 'inserting ' + table + ' ' + str(data[0]) + ' ' + data[1] + ' ' + data[2] + ' ' + data[3]
            cur.execute('INSERT INTO ' + table + '(DTLONG,DDATE,DTIME,DVALUE,NOTES,FETCHDT,FETCHDATE,FETCHTIME) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', data)
        #print 'ignoring ' + table + ' ' + str(data[0]) + ' ' + data[1] + ' ' + data[2] + ' ' + data[3]
        cur.close()
        return
    def queryData(self, table, beginTime, endTime):
        cur = self.conn.cursor()
        cur.execute('SELECT DTLONG,DDATE,DTIME,DVALUE FROM ' + table + ' WHERE DTLONG>=? AND DTLONG<=? ORDER BY DTLONG', (beginTime, endTime))
        return cur.fetchall()
    def addSilverRmb(self, silverRmb):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO SILVERRMB(DTLONG,DDATE,DTIME,DVALUE,NOTES,FETCHDT,FETCHDATE,FETCHTIME) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', silverRmb)
        cur.close()
    def querySilverRmb(self, beginTime, endTime):
        cur = self.conn.cursor()
        cur.execute('SELECT DTLONG,DDATE,DTIME,DVALUE FROM SILVERRMB WHERE DTLONG>=? AND DTLONG<=? ORDER BY DTLONG', (beginTime, endTime))
        return cur.fetchall()
    def addGoldUsd(self, goldUsd):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO GOLDUSD(DTLONG,DDATE,DTIME,DVALUE,NOTES,FETCHDT,FETCHDATE,FETCHTIME) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', goldUsd)
        cur.close()
    def queryGoldUsd(self, beginTime, endTime):
        cur = self.conn.cursor()
        cur.execute('SELECT DTLONG,DDATE,DTIME,DVALUE FROM GOLDUSD WHERE DTLONG>=? AND DTLONG<=? ORDER BY DTLONG', (beginTime, endTime))
        return cur.fetchall()
    def addAgTd(self, agTd):
        cur = self.conn.cursor()
        cur.execute('SELECT DTLONG FROM AGTD WHERE DTLONG=?', (long(agTd[0]),))
        if cur.fetchone() == None:
            #print 'inserting'
            cur.execute('INSERT INTO AGTD(DTLONG,DDATE,DTIME,DVALUE,VOLUME,FETCHDT,FETCHDATE,FETCHTIME) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', agTd)
        #print 'ignoring'
        cur.close()
        return
    def queryAgTd(self, beginTime, endTime):
        cur = self.conn.cursor()
        cur.execute('SELECT DTLONG,DDATE,DTIME,DVALUE,VOLUME FROM AGTD WHERE DTLONG>=? AND DTLONG<=? ORDER BY DTLONG', (beginTime, endTime))
        return cur.fetchall()
    def addUsdx(self, usdx):
        cur = self.conn.cursor()
        cur.execute('SELECT DTLONG FROM USDX WHERE DTLONG=?', (long(usdx[0]),))
        if cur.fetchone() == None:
            print 'inserting usdx ' + str(usdx[0]) + ' ' + usdx[1] + ' ' + usdx[2] + ' ' + usdx[3]
            cur.execute('INSERT INTO USDX(DTLONG,DDATE,DTIME,DVALUE,NOTES,FETCHDT,FETCHDATE,FETCHTIME) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', usdx)
        #print 'ignoring usdx ' + str(usdx[0]) + ' ' + usdx[1] + ' ' + usdx[2] + ' ' + usdx[3]
        cur.close()
        return
    def queryUsdx(self, beginTime, endTime):
        cur = self.conn.cursor()
        cur.execute('SELECT DTLONG,DDATE,DTIME,DVALUE FROM USDX WHERE DTLONG>=? AND DTLONG<=? ORDER BY DTLONG', (beginTime, endTime))
        return cur.fetchall()
    def commit(self):
        self.conn.commit()
    def closedb(self):
        self.conn.commit()
        self.conn.close()

