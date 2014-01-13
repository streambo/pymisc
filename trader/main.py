# -*- coding: utf-8 -*-
import datetime, time, csv, os, shutil
from utils.db import SqliteDB
from utils.rwlogging import log
from trader import Trader
import dataloader
from indicator import ma, macd, bolling, rsi, kdj
from strategy import maTrader, bollingTrader

path = os.path.dirname(__file__)

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
	prices = dataloader.importToArray('XAGUSD1440_ALL')
	maTrader.runStrategy(prices)
	#importAll()
	#importTable('XAGUSD1440')
	#maTrader.runStrategy('XAGUSD1440')
	#bollingTrader.runStrategy('XAGUSD1440')
	
	#calculateIndicators('XAGUSD1440')
	#strategyMA()
	#strategyBolling()



