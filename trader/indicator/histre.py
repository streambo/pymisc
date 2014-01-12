# -*- coding: utf-8 -*-
import os
import pylab as pl
from utils.rwlogging import log

path = os.path.dirname(__file__)

class HistoryTrend():
	def __init__(self):
		self.days = 36
		self.expect = 12
		self.histred = ''
		self.history= []
	
	def buildTrend(self, prices):
		if len(prices) <= 1:
			self.history.append(prices[len(prices) - 1])
			return
		
		self.history.append(prices[len(prices) - 1])
		cur = prices[len(prices) - 1]['pc']
		pre = prices[len(prices) - 2]['pc']
		#log.info('Trends ' + str(cur) + ' - ' + str(pre))
		if cur < pre:
			self.histred = self.histred + 'D'
		else:
			self.histred = self.histred + 'U'
		#log.info('Trends ' + self.histred)
		
	def graphic(self, cur, his):
		cdt = cur[len(cur) - 1]['dt'].strftime('%Y%m%d-%H%M')
		hdt = his[len(his) - 1]['dt'].strftime('%Y%m%d-%H%M')
		t = cdt + '_' + hdt
		
		x = []
		y1 = []
		y2 = []
		for i in range(0, len(cur)):
			x.append(i)
			y1.append(cur[i]['pc'])
			y2.append(his[i]['pc'])
		
		pl.clf()
		pl.plot(x, y1, 'r')
		pl.plot(x, y2, 'g')
		pl.title(t)
		#pl.show()
		pl.savefig(os.path.join(path, 'result/' + t + '.png'))
			
		
	def analysis(self, prices):
		self.buildTrend(prices)
		
		if len(prices) <= self.days:
			return
			
		current = prices[len(prices) - self.days - 1 : len(prices)]
		#log.info(current)
		
		chour = current[len(current) - 1]['dt'].hour
		cdt = current[len(current) - 1]['dt'].strftime('%Y-%m-%d %H:%M')
		
		ct = ''
		for i in range(1, len(current)):
			cur = current[i]['pc']
			pre = current[i - 1]['pc']
			#log.info('Current ' + str(cur) + ' - ' + str(pre))
			if cur < pre:
				ct = ct + 'D'
			else:
				ct = ct + 'U'
			#log.info('Current ' + ct)
		
		for i in range(self.days, len(self.history) - self.days):
			his = self.history[i - self.days : i + 1]
			hhour = his[len(his) - 1]['dt'].hour
			if abs(chour - hhour) > 2:
				continue
			ht = self.histred[i - self.days : i]
			#if similar(ct, ht) < 3:
			if ct[0 : self.days - self.expect] == ht[0 : self.days - self.expect]:
				self.graphic(current, his)
				curChange = current[len(current) - self.expect - 1]['pc'] - current[len(current) - self.days - 1]['pc']
				hisChange = his[len(his) - self.expect - 1]['pc'] - his[len(his) - self.days - 1]['pc']
				hdt = his[len(his) - 1]['dt'].strftime('%Y-%m-%d %H:%M')
				log.info('History Date:' + hdt + ', Trend: ' + ht + ',change:' + str(hisChange))
				log.info('Current Date:' + cdt + ', Trend: ' + ct + ',change:' + str(curChange))
				curChange = current[len(current) - 1]['pc'] - current[len(current) - self.expect - 1]['pc']
				hisChange = his[len(his) - 1]['pc'] - his[len(his) - self.expect - 1]['pc']
				log.info('history:' + ht[self.days - self.expect:] + ',change:' + str(hisChange))
				log.info('verify:' +  ct[self.days - self.expect:] + ',change:' + str(curChange))
				log.info('=========================')
			
		
			
	