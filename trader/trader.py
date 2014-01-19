# -*- coding: utf-8 -*-
import os, datetime
from numpy import array
import pylab as pl
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import DateFormatter
from matplotlib.widgets import MultiCursor

from utils.rwlogging import tradeLogger as logt
from utils.rwlogging import balLogger as logb
from utils.rwlogging import tradesLogger as logtr
from utils.rwlogging import strategyLogger as logs

class Counter():
	def __init__(self, no):
		self.no = str(no)
		self.isActive = False
		self.posNum = 0
		self.position = 0
		self.direction = 0  #0 none, 1 buy, -1 sell
		self.args = []
		

class Trader():
	def __init__(self, strategyName):
		self.initBalance = 20000.00
		self.fee = 0.01
		self.volumeSize = 1000
		
		plt.rcParams.update({'axes.labelsize':10})
		plt.rcParams.update({'xtick.labelsize':8})
		plt.rcParams.update({'ytick.labelsize':8})
		
		self.strategyName = strategyName
		self.balance = self.initBalance
		self.equity = self.initBalance
		self.position = 0
		self.counters = [Counter(0), Counter(1), Counter(2), ]
		self.counters[0].isActive = True
		
		self.stats = {}
		self.stats['lastDate'] = '1900-01-01'
		self.stats['lastEquity'] = self.initBalance
		self.stats['downDays'] = 0
		self.stats['date'] = []
		self.stats['equity'] = []
		self.stats['balance'] = []
		self.stats['position'] = []
		self.stats['price'] = []
		self.stats['buy'] = {}
		self.stats['buy']['date'] = []
		self.stats['buy']['price'] = []
		self.stats['sell'] = {}
		self.stats['sell']['date'] = []
		self.stats['sell']['price'] = []
		self.stats['log'] = []
		
	def switchActiveCounter(self, cntNo, dt, price):
		if self.counters[cntNo].isActive: return
		
		for counter in self.counters:
			counter.isActive = False
		
		self.counters[cntNo].isActive = True
		
		if self.counters[cntNo].direction == 1:
			self.buy(dt, price, cntNo=cntNo, notes='SWITCH')
		
		if self.counters[cntNo].direction == -1:
			self.sell(dt, price, cntNo=cntNo, notes='SWITCH')
		
	def show(self, dt, price):
		ddate = dt.strftime('%Y-%m-%d')
		
		if ddate == self.stats['lastDate']: return
		self.stats['lastDate'] = ddate
		
		self.position = 0
		for counter in self.counters:
			self.position += counter.position;
	
		if self.position < 0:
			self.equity = self.balance + self.position * (price + self.fee)
		else:
			self.equity = self.balance + self.position * (price - self.fee)
			
		if self.equity < self.stats['lastEquity']: self.stats['downDays'] += 1
		self.stats['lastEquity'] = self.equity
		self.stats['date'].append(dt)
		self.stats['equity'].append(self.equity)
		self.stats['balance'].append(self.balance)
		self.stats['position'].append(self.position)
		self.stats['price'].append(price)
		
	def buy(self, dt, price, cntNo = 0, notes='', closing = False):
		vol = self.volumeSize
		counter = self.counters[cntNo]
		
		if not counter.isActive:
			counter.direction = 1
			closing = True
		else:
			counter.direction = 0
		
		if closing and counter.posNum >= 0:
			return
		elif closing and counter.posNum < 0:
			vol = 0 - counter.position
			counter.posNum = 0
		elif counter.posNum < 0:
			vol = vol - counter.position;
			counter.posNum = 1
		else:
			counter.posNum += 1
			
		counter.position = counter.position + vol
		self.balance = self.balance - vol * (price + self.fee)
		self.stats['buy']['date'].append(dt)
		self.stats['buy']['price'].append(price)
		dtstr = dt.strftime('%Y-%m-%d %H:%M')
		self.stats['log'].append('BUY,' + self.strategyName + ',' + dtstr + ',' + counter.no + ',' + str(price) + ',' + str(vol) + ',' + str(counter.position) + ',' + notes)
		
	def sell(self, dt, price, cntNo = 0, notes='', closing = False):
		vol = self.volumeSize
		counter = self.counters[cntNo]
		
		if not counter.isActive:
			counter.direction = -1
			closing = True
		else:
			counter.direction = 0
		
		if closing and counter.posNum <= 0:
			return
		elif closing and counter.posNum > 0:
			vol = counter.position
			counter.posNum = 0
		elif counter.posNum > 0:
			vol = vol + counter.position;
			counter.posNum = -1
		else:
			counter.posNum -= 1
		
		counter.position = counter.position - vol
		self.balance = self.balance + vol * (price - self.fee)
		
		self.stats['sell']['date'].append(dt)
		self.stats['sell']['price'].append(price)
		dtstr = dt.strftime('%Y-%m-%d %H:%M')
		self.stats['log'].append('SELL,' + self.strategyName + ',' + dtstr + ',' + counter.no + ',' + str(price) + ',' + str(vol) + ',' + str(counter.position) + ',' + notes)
	
	def generateGraph(self, rate = 0):
		emax = max(self.stats['equity'])
		emin = min(self.stats['equity'])
		
		fig = plt.figure()
		ax1 = fig.add_subplot(211)
		#ax1 = plt.subplot2grid((7, 1), (0, 0), rowspan=3)
		ax1.set_ylabel('Equity')
		ax1.plot_date(self.stats['date'], self.stats['equity'], color='r', linestyle='-', marker='', label='Equity')
		#ax1.grid()
		ax1.xaxis.set_major_formatter(DateFormatter('%m-%d'))
		ax1.vlines(self.stats['buy']['date'], emin, emax, color='y', linestyles ='dotted')
		ax1.vlines(self.stats['sell']['date'], emin, emax, color='g', linestyles ='dotted')
		
		ax2 = fig.add_subplot(212)
		#ax2 = plt.subplot2grid((7, 1), (3, 0), rowspan=3)
		ax2.set_ylabel('Price')
		ax2.plot_date(self.stats['date'], self.stats['price'], color='black', linestyle='-', marker='', label='Price')
		ax2.plot_date(self.stats['buy']['date'], self.stats['buy']['price'], color='r', linestyle='', marker='^')
		ax2.plot_date(self.stats['sell']['date'], self.stats['sell']['price'], color='b', linestyle='', marker='v')
		#ax2.grid()
		ax2.xaxis.set_major_formatter(DateFormatter('%m-%d'))
		
		if rate > 0:
			fname = str(rate) + '_' + self.strategyName
		else:
			fname = self.strategyName
			
		plt.savefig(os.path.join(os.path.dirname(__file__), 'result/' + fname + '.png'), dpi=150)
		plt.close(fig)
		return
		