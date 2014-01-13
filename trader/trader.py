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

class Trader():
	def __init__(self, strategyName):
		self.initBal = 20000.00
		self.fee = 0.02
		
		self.strategyName = strategyName
		self.bal = self.initBal
		self.position = 0
		self.bsflag = 0
		
		self.lastEquity = self.initBal
		self.lastbdate = '1900-01-01'
		self.bdts = []
		self.bequity = []
		self.bbalance = []
		self.bprices = []
		self.bbuyDates = []
		self.bsellDates = []
		self.bbuyPrices = []
		self.bsellPrices = []
	def show(self, ddate, dtime, price):
	
		if self.position < 0:
			self.equity = self.bal + self.position * (price + self.fee)
		else:
			self.equity = self.bal + self.position * (price - self.fee)
			
		if ddate != self.lastbdate:
			self.bdts.append(ddate + ' ' + dtime)
			self.bequity.append(self.equity)
			self.bbalance.append(self.bal)
			self.bprices.append(price)
			
		if self.equity == self.lastEquity:
			chan = 'FAIR'
		elif self.equity > self.lastEquity:
			chan = 'UP'
		elif self.equity < self.lastEquity:
			chan = 'DOWN'
		
		#logb.info('STATUS,' + self.strategyName + ',' + ddate + ',' + dtime + ',' + 
str(self.equity) + ',' + str(chan) + ',' + str(self.bal) + ',' + str(self.position) + ',' + str(price))
		
	def buy(self, ddate, dtime, price, notes='', closing = False):
		vol = 1000
		self.bsflag += 1
		if self.position < 0:
			vol = 1000 - self.position
			self.bsflag = 1
		
		if closing:
			if self.position < 0:
				vol = self.position
				self.bsflag = 0
			else:
				return
			
		self.bal = self.bal - vol * (price + self.fee)
		self.position = self.position + vol
		#logtr.info('BUY,' + self.strategyName + ',' + ddate + ',' + dtime + ',,,' + str(vol) + ',' + str(price) + ',' + notes)
		
		self.bbuyDates.append(ddate + ' ' + dtime)
		self.bbuyPrices.append(price)
		return
	def sell(self, ddate, dtime, price, notes='', closing = False):
		vol = 1000
		self.bsflag -= 1
		if self.position > 0:
			vol = 1000 + self.position
			self.bsflag = -1
			
		if closing:
			if self.position > 0:
				vol = self.position
				self.bsflag = 0
			else:
				return
		
		self.bal = self.bal + vol * (price - self.fee)
		self.position = self.position - vol
		#logtr.info('SELL,' + self.strategyName + ',' + ddate + ',' + dtime + ',,,' + str(vol) + ',' + str(price) + ',' + notes)
		self.bsellDates.append(ddate + ' ' + dtime)
		self.bsellPrices.append(price)
		return

	def generateGraph(self):
		#if self.equity < self.initBal + 0.2 * self.initBal: return
	
		dts = [datetime.datetime.strptime(self.bdts[i], '%Y-%m-%d %H:%M:%S') for i in range(len(self.bdts))]
		buydts = [datetime.datetime.strptime(self.bbuyDates[i], '%Y-%m-%d %H:%M:%S') for i in range(len(self.bbuyDates))]
		selldts = [datetime.datetime.strptime(self.bsellDates[i], '%Y-%m-%d %H:%M:%S') for i in range(len(self.bsellDates))]
		emax = max(self.bequity)
		emin = min(self.bequity)
		pmax = max(self.bprices)
		pmin = min(self.bprices)
		
		#mpl.rc('xtick', labelsize=8)
		#mpl.rc('ytick', labelsize=8)
		plt.rcParams.update({'axes.labelsize':10})
		plt.rcParams.update({'xtick.labelsize':8})
		plt.rcParams.update({'ytick.labelsize':8})
		
		#plt.clf()
		fig = plt.figure()
		#ax1 = plt.subplot2grid((7, 1), (0, 0), rowspan=3)
		ax1 = fig.add_subplot(211)
		ax1.set_ylabel('Equity')
		ax1.plot_date(dts, self.bequity, color='r', linestyle='-', marker='', label='Equity')
		#ax1.grid()
		ax1.xaxis.set_major_formatter(DateFormatter('%m-%d'))
		ax1.vlines(buydts, emin, emax, color='y', linestyles ='dotted')
		ax1.vlines(selldts, emin, emax, color='g', linestyles ='dotted')
		
		#ax2 = plt.subplot2grid((7, 1), (3, 0), rowspan=3)
		ax2 = fig.add_subplot(212)
		ax2.set_ylabel('Price')
		ax2.plot_date(dts, self.bprices, color='black', linestyle='-', marker='', label='Price')
		ax2.plot_date(buydts, self.bbuyPrices, color='r', linestyle='', marker='^')
		ax2.plot_date(selldts, self.bsellPrices, color='b', linestyle='', marker='v')
		#ax2.grid()
		ax2.xaxis.set_major_formatter(DateFormatter('%m-%d'))
		
		#ax3 = plt.subplot2grid((7, 1), (6, 0))
		#ax3 = fig.add_subplot(313)
		#ax3.plot_date(dts, self.bbalance, color='b', linestyle='-', marker='', label='Balance')
		#ax3.xaxis.set_major_formatter(DateFormatter('%m-%d'))
		
		#multi = MultiCursor(fig.canvas, (ax1, ax2), color='r', lw=1, horizOn=False, vertOn=True)
		#plt.show()
		plt.savefig(os.path.join(os.path.dirname(__file__), 'result/' + self.strategyName + '.png'), dpi=150)
		plt.close(fig)
		return
		
		