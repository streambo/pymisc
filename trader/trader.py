# -*- coding: utf-8 -*-
import os
from numpy import array
import pylab as pl
from utils.db import SqliteDB
from utils.rwlogging import tradeLogger as log

class Trader():
	def __init__(self):
		self.bal = 10000.00
		self.fee = 0.02
		self.position = 0
		
		self.lastbdate = '1900-01-01'
		self.bdates = []
		self.btotals = []
		self.bposs = []
		self.bprices = []
	def show(self, ddate, dtime, price):
		if self.position < 0:
			total = self.bal + self.position * (price + self.fee)
		else:
			total = self.bal + self.position * (price - self.fee)
			
		if ddate != self.lastbdate:
			self.bdates.append(ddate)
			self.btotals.append(total)
			self.bposs.append(self.position)
			self.bprices.append(price)
		log.info('STATUS,' + ddate + ',' + dtime + ',' + str(total) + ',' + str(self.bal) + ',' + str(self.position) + ',' + str(price))
		
	def buy(self, ddate, dtime, price):
		vol = 1000
		if self.position < 0:
			vol = 1000 - self.position
		self.bal = self.bal - vol * (price + self.fee)
		self.position = self.position + vol
		log.info('BUY,' + ddate + ',' + dtime + ',,,' + str(vol) + ',' + str(price))
		return
	def sell(self, ddate, dtime, price):
		vol = 1000
		if self.position > 0:
			vol = 1000 + self.position
		self.bal = self.bal + vol * (price - self.fee)
		self.position = self.position - vol
		log.info('SELL,' + ddate + ',' + dtime + ',,,' + str(vol) + ',' + str(price))
		return

	def generateGraph(self):
		indx = [i for i in range(len(self.btotals))]
		pl.clf()
		pl.plot(indx, self.btotals)
		pl.title('Total Change')
		pl.savefig(os.path.join(os.path.dirname(__file__), 'result/total.png'))
		
		pl.clf()
		pl.plot(indx, self.bprices, 'r')
		pl.title('Price Change')
		pl.savefig(os.path.join(os.path.dirname(__file__), 'result/price.png'))
		
		pl.clf()
		pl.plot(indx, self.bposs)
		pl.title('Position Change')
		pl.savefig(os.path.join(os.path.dirname(__file__), 'result/position.png'))

