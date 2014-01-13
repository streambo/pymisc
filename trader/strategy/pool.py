# -*- coding: utf-8 -*-
from utils.rwlogging import tradeLogger as logt
from utils.rwlogging import balLogger as logb
from utils.rwlogging import tradesLogger as logtr
from utils.rwlogging import strategyLogger as logs

class StrategyPool():
	def __init__(self, num):
		self.num = num
		self.strategies = [['', 0, 0, 0, 0]]
		
	def estimate(sname, equity, buynum, sellnum, t):
		
		l = len(self.strategies)
		for i in range(l):
			if (equity > self.strategies[i][1]):
				logt.info(sname + ',' + str(buynum) + ',' + str(sellnum) + ',' + str(equity))
				self.strategies.insert(i, [sname, equity, buynum, sellnum, t])
				if l + 1 > self.num:
					self.strategies.pop(-1)
				break
	
	def showStrategies():
		for s in self.strategies:
			logs.info(s[0] + ',' + str(s[2]) + ',' + str(s[3]) + ',' + str(s[1]))
			s[4].generateGraph()
