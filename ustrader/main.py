# -*- coding: utf-8 -*-
import datetime, time, csv, os, shutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor
from utils.db import SqliteDB
from utils.rwlogging import log
from trader import Trader
import dataloader
from indicator import ma, macd, bolling, rsi, kdj
from strategy import maTrader, bollingTrader, macdTrader, rsiTrader, kdjTrader
from strategy import n2Trader, n3Trader, s3Trader, s4Trader, s5Trader, s6Trader
from strategy import l5Trader
from mas import maStrategy, fmaStrategy

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
	
	
def drawStats(prices):
	
	for i in range(5, 51):
		drawStat(prices, i)

def drawStat(prices, period):
	
	l = len(prices)
	ps = [0] * l
	pdts = [0] * l
	std = [0] * l
	stdper = [0] * l
	diff = [0] * l
	dmean = [0] * l
	
	days = 0
	for i in range(l):
		pdts[i] = prices[i]['dt']
		ps[i] = prices[i]['close']
		diff[i] = prices[i]['high'] - prices[i]['low']
		if i < period - 1: continue
		std[i] = round(np.std(ps[i-period+1 : i+1], dtype=np.float64, ddof=0), 3)
		stdper[i] = round(std[i] / np.mean(ps[i-period+1 : i+1]), 3)
		dmean[i] = round(np.mean(diff[i-period+1 : i+1]), 3)
		
		if (std[i-1] < 1 and std[i] >= 1) or (std[i-1] > 1 and std[i] <= 1):
			dtstr = prices[i]['dt'].strftime('%Y-%m-%d')
			log.info(dtstr + ', std change to ' + str(std[i]) + ', days: ' + str(days))
			days = 0
		days += 1
		
	macds = macd.calc_macd(prices, 12, 26, 9)
	
	fig = plt.figure()
	ax1 = fig.add_subplot(311)
	ax1.set_ylabel('Price')
	ax1.grid()
	ax1.plot_date(pdts, ps, color='b', linestyle='-', marker='', label='Equity')
	
	ax2 = fig.add_subplot(312)
	ax2.set_ylabel('Std')
	ax2.grid()
	ax2.plot_date(pdts, std, color='b', linestyle='-', marker='', label='Equity')
	
	ax3 = fig.add_subplot(313)
	ax3.set_ylabel('MACD')
	ax3.grid()
	ax3.plot_date(pdts, stdper, color='b', linestyle='-', marker='', label='Equity')
	
	#multi = MultiCursor(fig.canvas, (ax1, ax2, ax3), color='r', lw=1, horizOn=False, vertOn=True)
	#plt.show()
	#return
	fname = str(period)
		
	plt.savefig(os.path.join(os.path.dirname(__file__), 'result/' + fname + '.png'), dpi=150)
	plt.close(fig)
	return
		

def clearLog():
	logdir = os.path.join(path, 'logs')
	rsdir = os.path.join(path, 'result')
	
	rslist = os.listdir(rsdir)
	for f in rslist:
		fp = os.path.join(rsdir, f)
		if os.path.isfile(fp):
			os.remove(fp)
			#log.debug('del' + fp)
		elif os.path.isdir(fp):
			shutil.rmtree(fp)
	
	logfiles =['trader.csv', 'balance.csv', 'trades.csv', 'strategy.csv', 'main.log',]
	for logfile in logfiles:
		with open(os.path.join(logdir, logfile), 'w'):
			pass
	#print logdir, lsdir
	#shutil.rmtree(logdir)
	#os.mkdir(logdir)
	
if __name__ == "__main__":
	#XAGUSD1440_FLUC, XAGUSD1440_UP, XAGUSD1440_DOWN, XAGUSD1440_V, XAGUSD1440_RV, 
	#XAGUSD1440_FLAT, XAGUSD1440_FLU
	#XAGUSD1440_2013, XAGUSD1440_2012, XAGUSD1440_2011, XAGUSD1440_ALL, XAGUSD1440_AFTER08
	clearLog()
	prices = dataloader.importToArray('XAUUSD60_20122013')
	maStrategy.runStrategy(prices)
	#s6Trader.runStrategy(prices)
	#l5Trader.runStrategy(prices)
	#maTrader.runStrategy(prices)
	#drawStats(prices)
	#oneTrader.runStrategy(prices)
	#part = prices[109:]
	#ps = [p['close'] for p in part]
	#ps.reverse() 
	#pr = [p['rmb'] for p in part]
	#pr.reverse() 
	#
	#for i in range(len(part)):
	#	part[i]['close'] = ps[i]
	#	part[i]['rmb'] = pr[i]
	
	#maTrader.runStrategy(prices, 0)
	#drawStats(prices)
	#kdjTrader.runStrategy(prices)
	#bollingTrader.runStrategy(prices)
	#maTrader.runStrategy(prices, 112) #XAGUSD1440_FLAT
	#maTrader.runStrategy(prices, 109) #XAGUSD1440_FLU
	#rsiTrader.runStrategy(prices)
	#macdTrader.runStrategy(prices)
	#importAll()
	#importTable('XAGUSD1440')
	#maTrader.runStrategy('XAGUSD1440')
	#bollingTrader.runStrategy('XAGUSD1440')
	
	#calculateIndicators('XAGUSD1440')
	#strategyMA()
	#strategyBolling()



