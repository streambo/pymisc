# -*- coding: utf-8 -*-
import datetime, time, csv, os, shutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor
from utils.db import SqliteDB
from utils.rwlogging import log
import dataloader
from indicator import ma, macd, bolling, rsi, kdj
from voters import l1voter, l2voter, pool, maVoter, macdVoter, rsiVoter

path = os.path.dirname(__file__)

def drawStat(prices):
	
	l = len(prices)
	directs, slopes, stds, areas = pool.calc_variants(prices)
		
	dts = [p['dt'] for p in prices]
	ps = [p['close'] for p in prices]
	fig = plt.figure()
	ax1 = fig.add_subplot(211)
	ax1.plot_date(dts, areas, 'r-')
	ax1.set_ylim(-1, 4)
	#ax1.plot_date(dts, stds, 'r-')
	
	ax2 = fig.add_subplot(212)
	ax2.plot_date(dts, ps, 'b-')
	
	plt.show()
	


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
	
	
if __name__ == "__main__":
	#return
	#XAGUSD1440_FLUC, XAGUSD1440_UP, XAGUSD1440_DOWN, XAGUSD1440_V, XAGUSD1440_RV, 
	#XAGUSD1440_FLAT, XAGUSD1440_FLU
	#XAGUSD1440_2013, XAGUSD1440_2012, XAGUSD1440_2011, XAGUSD1440_ALL, XAGUSD1440_AFTER09
	clearLog()
	prices = dataloader.importToArray('XAGUSD1440_2013')
	#drawStat(prices)
	#maVoter.runVoter(prices)
	#macdVoter.runVoter(prices)
	#rsiVoter.runVoter(prices)
	
	l2voter.runVoter(prices)
	