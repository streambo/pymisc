# -*- coding: utf-8 -*-
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import tradesLogger as logtr

class StrategyPool():
	def __init__(self, num):
		self.num = num
		self.strategies = [[0, 0]]
		
	def estimate(self, t):
		
		l = len(self.strategies)
		if t.equity <= self.strategies[-1][1]: return
		for i in range(l):
			if (t.equity > self.strategies[i][1]):
				log.info(t.strategyName + ',' + str(len(t.bbuyDates)) + ',' + str(len(t.bsellDates)) + ',' + str(t.equity))
				self.strategies.insert(i, [t, t.equity])
				if l + 1 > self.num:
					self.strategies.pop(-1)
				break
	
	def showStrategies(self):
		i = 1
		for s in self.strategies:
			if s[0] == 0: break
			logs.info(s[0].strategyName + ',' + str(len(s[0].bbuyDates)) + ',' + str(len(s[0].bsellDates)) + ',' + str(s[1]))
			for j in range (len(s[0].bbuyDates))
				logtr.info(s[0].strategyName + ',' + s[0].bbuyDates[j] + ',' + str(s[0].bbuyPrices[i]))
				
			for j in range (len(s[0].bsellDates))
				logtr.info(s[0].strategyName + ',' + s[0].bsellDates[j] + ',' + str(s[0].bsellPrices[i]))
			s[0].generateGraph(i)
			i += 1
