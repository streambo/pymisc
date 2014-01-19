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
				log.info(t.strategyName + ',' + str(len(t.stats['buy']['date'])) + ',' + str(len(t.stats['sell']['date'])) + ',' + str(t.stats['downDays']) + ',' + str(t.equity))
				self.strategies.insert(i, [t, t.equity])
				if l + 1 > self.num:
					self.strategies.pop(-1)
				break
	
	def showStrategies(self):
		rate = 1
		logs.info('STRATEGY,BUY TIMES, SELL TIMES, DOWN DAYS, FINAL EQUITY')
		logtr.info('OP,STRATEGY,TIME,COUNTER,PRICE,VOLUMN,POSITION,NOTES')
		for s in self.strategies:
			if s[0] == 0: break
			logs.info(s[0].strategyName + ',' + str(len(s[0].stats['buy']['date'])) + ',' + str(len(s[0].stats['sell']['date'])) + ',' + str(s[0].stats['downDays']) + ',' + str(s[1]))
			for tl in s[0].stats['log']:
				logtr.info(tl)
				
			s[0].generateGraph(rate)
			rate += 1
