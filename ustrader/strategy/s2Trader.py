# -*- coding: utf-8 -*-
import datetime, time, csv, os
import numpy as np
from utils.db import SqliteDB
from utils.rwlogging import log
from utils.rwlogging import strategyLogger as logs
from utils.rwlogging import balLogger as logb
from trader import Trader
from indicator import ma, macd, bolling, rsi, kdj
from strategy.pool import StrategyPool


def runStrategy(in_prices):
	log.debug('beginning one strategy ...')


	prices = in_prices
	ps = [p['close'] for p in prices]


	slopePeriod = 50
	l = len(prices)
	slopes = [0] * l
	stds = [0] * l
	for i in range(slopePeriod, l):
		slopes[i] = calc_slope(ps[i-slopePeriod+1 : i+1])
		stds[i] = round(np.std(ps[i-slopePeriod+1 : i+1], dtype=np.float64, ddof=0), 3)


	found = 0
	for i in range(1055, l):
		curSlope = slopes[i]
		curStd = stds[i]
		minDiffSlope = minDiffStd = 999
		jslope = jstd = 0
		for j in range(slopePeriod, i - 20):
			diffSlope = abs(slopes[j] - curSlope)
			diffStd = abs(stds[j] - curStd)
			if diffSlope <= 0.001 and diffStd <= 0.005:
				minDiffSlope, jslope = diffSlope, j
				minDiffStd, jstd = diffStd, j
				found += 1
				break
		#log.debug('i :' + str(i) + ',' + str(curSlope) + ',' + str(curStd) + ', min diff slope,' + str(jslope) + ':' + str(minDiffSlope) + ', min diff std,' + str(jstd) + ':' + str(minDiffStd))
		log.debug('i :' + str(prices[i]['dt']) + ', j :' + str(prices[jslope]['dt']))
	log.debug('total:' + str(l - slopePeriod) + ',found:' + str(found))
	


def calc_slope(datas):
	l = len(datas)
	xs = np.arange(l)
	xsT = np.array([xs, np.ones(l)]).T
	m, c = np.linalg.lstsq(xsT, datas)[0]
	return round(m, 3)

