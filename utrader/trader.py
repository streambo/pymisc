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

def checkTime(dt):
	return True
	td = datetime.timedelta(hours=6)
	ndt = dt + td
	#print ndt.weekday, ndt.hour
	if ndt.weekday() >= 5:
		return False
	
	if ndt.hour in [9, 10, 21, 22, 23, ]:
		return True
	
	if ndt.hour in [11, 15, ] and ndt.minute < 30:
		return True
	
	if ndt.hour in [13, ] and ndt.minute >= 30:
		return True
		
	return False
	

class Counter():
	def __init__(self, trader, no):
		self.trader = trader
		self.no = str(no)
		self.isActive = False
		self.position = 0
		self.wait = 0  #0 none, 1 buy, -1 sell
		self.args = []
		
	def caculateVolume(self, dt, price, volume, notes='', closing=False):
		isGoodTime = checkTime(dt)
		
		opos = self.position
		owait = self.wait
		total = self.position + self.wait
		
		if isGoodTime and self.isActive:
			if volume * total >= 0:
				if not closing:
					self.position = volume + total
					self.wait = 0
			else:
				if closing:
					self.position = 0
					self.wait = 0
				else:
					self.position = volume
					self.wait = 0
		elif isGoodTime: # can trade but inactive
			if volume * total >= 0:
				if not closing:
					self.wait += volume
			else:
				if closing:
					self.position = 0
					self.wait = 0
				else:
					self.position = 0
					self.wait = volume
		else: # cannot trade 
			if volume * total >= 0:
				if not closing:
					self.wait += volume
			else:
				if closing:
					self.wait = 0 - self.position
				else:
					self.wait = volume - self.position
					
		volume = self.position - opos
		if not(self.position == opos and self.wait == owait):
			cname = self.no
			if isGoodTime: cname += '_G'
			if self.isActive: cname += '_A'
			dtstr = dt.strftime('%Y-%m-%d %H:%M')
			self.trader.stats['log'].append('ORDER,' + self.trader.strategyName + ',' + dtstr + ',' + cname + ',' + str(price) + ',' + str(volume) + ', POS: ' + str(opos) + '->' + str(self.position) + ', WAIT: ' + str(owait) + '->' + str(self.wait) + ',' + notes)
			
		return volume
		
class Trader():
	def __init__(self, strategyName):
		self.initBalance = 20000.00
		#self.feeRate = 0.0008
		self.fee = 0.02
		
		plt.rcParams.update({'axes.labelsize':10})
		plt.rcParams.update({'xtick.labelsize':8})
		plt.rcParams.update({'ytick.labelsize':8})
		
		self.strategyName = strategyName
		self.balance = self.initBalance
		self.equity = self.initBalance
		self.position = 0
		self.counters = [Counter(self, 0), Counter(self, 1), Counter(self, 2), Counter(self, 3), ]
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
		
	def processOrder(self, dt, price, volume, cntNo=0, notes='', closing=False):
		counter = self.counters[cntNo]
		volume = counter.caculateVolume(dt, price, volume, notes, closing)
		
		if volume > 0:
			self.balance = self.balance - volume * (price + self.fee)
			#self.stats['log'].append(str(self.balance))
			self.stats['buy']['date'].append(dt)
			self.stats['buy']['price'].append(price)
			
		elif volume < 0:
			self.balance = self.balance - volume * (price - self.fee)
			#self.stats['log'].append(str(self.balance))
			self.stats['sell']['date'].append(dt)
			self.stats['sell']['price'].append(price)
			
		self.show(dt, price)
		
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
		