# -*- coding: utf-8 -*-
import os, datetime
import numpy as np
import matplotlib.pyplot as plt
import dataloader
import ols
from multipolyfit import multipolyfit, mk_sympy_function
from utils.rwlogging import log

path = os.path.dirname(__file__)

def testCo(co):
	xagPrices = dataloader.importToArray('XAGUSD5_201307')
	xags = [p['close'] for p in xagPrices]
	
	usdxPrices = dataloader.importToArray('_USDX5_201307')
	usdxs = [p['close'] for p in usdxPrices]
	
	us500Prices = dataloader.importToArray('_US5005_201307')
	us500s = [p['close'] for p in us500Prices]
	
	us30Prices = dataloader.importToArray('_US305_201307')
	us30s = [p['close'] for p in us30Prices]
	
	nq100Prices = dataloader.importToArray('_NQ1005_201307')
	nq100s = [p['close'] for p in nq100Prices]
	
	l = len(xagPrices)
	xs = []
	ys = []
	yps = []
	typs = []
	#for i in range(10, l - 1):
	for i in range(100, 200):
		xag = xagPrices[i]
		xagd = xags[i-10+1 : i+1]
		dtlong = xag['dtlong']
		usdxd = findData(dtlong, usdxPrices, usdxs)
		us500d = findData(dtlong, us500Prices, us500s)
		us30d = findData(dtlong, us30Prices, us30s)
		nq100d = findData(dtlong, nq100Prices, nq100s)
		
		if not (usdxd and us500d and us30d and nq100d):
			log.debug('Insufficient Data. ' + xag['date'] + ' ' + xag['time'])
			continue
		
		xs.append([xags[i], slope(xagd), std(xagd), slope(usdxd), std(usdxd), slope(us500d), std(us500d), slope(us30d), std(us30d), slope(nq100d), std(nq100d)])
		typs.append(xags[i])
		ys.append(xags[i+1])

	for i in range(len(xs)):
		yp = co[0] + xs[i][0] * co[1]
		yp += xs[i][1] * co[2] + xs[i][2] * co[3] + xs[i][3] * co[4]
		yp += xs[i][4] * co[5] + xs[i][5] * co[6] + xs[i][6] * co[7] + xs[i][7] * co[8]
		yp += xs[i][8] * co[9] + xs[i][9] * co[10] + xs[i][10] * co[11]
		yps.append(typs[i] + yp)
	
	print co
	ts = range(len(xs))
	plt.plot(ts, ys, 'o', label='Original data', linestyle='-', markersize=2)
	plt.plot(ts, yps, 'ro', label='Fitted line', linestyle='-', markersize=2)
	plt.legend()
	plt.show()
	
	
def regression():
	xagPrices = dataloader.importToArray('XAGUSD5_2013070809')
	xags = [p['close'] for p in xagPrices]
	
	usdxPrices = dataloader.importToArray('_USDX5_2013070809')
	usdxs = [p['close'] for p in usdxPrices]
	
	us500Prices = dataloader.importToArray('_US5005_2013070809')
	us500s = [p['close'] for p in us500Prices]
	
	us30Prices = dataloader.importToArray('_US305_2013070809')
	us30s = [p['close'] for p in us30Prices]
	
	nq100Prices = dataloader.importToArray('_NQ1005_2013070809')
	nq100s = [p['close'] for p in nq100Prices]
	
	
	l = len(xagPrices)
	xs = []
	ys = []
	for i in range(10, l - 1):
		xag = xagPrices[i]
		xagd = xags[i-10+1 : i+1]
		dtlong = xag['dtlong']
		usdxd = findData(dtlong, usdxPrices, usdxs)
		us500d = findData(dtlong, us500Prices, us500s)
		us30d = findData(dtlong, us30Prices, us30s)
		nq100d = findData(dtlong, nq100Prices, nq100s)
		
		if not (usdxd and us500d and us30d and nq100d):
			log.debug('Insufficient Data. ' + xag['date'] + ' ' + xag['time'])
			continue
		
		xs.append([xags[i], slope(xagd), std(xagd), slope(usdxd), std(usdxd), slope(us500d), std(us500d), slope(us30d), std(us30d), slope(nq100d), std(nq100d)])
		ys.append(xags[i+1] - xags[i])
		
	#print xs
	#print ys
	xxs = np.array(xs)
	#print xsT
	yys = np.array(ys)
	mymodel = multipolyfit(xxs.T, yys, 20, model_out = False)
	#mymodel = ols.ols(yys, xxs, 'y',['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10', 'x11'])
	#print mymodel.b
	print mymodel
	#print mymodel.summary()
	return mymodel
	
	yps = []
	co = mymodel.b
	for i in range(len(xs)):
		yp = co[0] + xs[i][0] * co[1] + xs[i][1] * co[2] + xs[i][2] * co[3] + xs[i][3] * co[4]
		yp += xs[i][4] * co[5] + xs[i][5] * co[6] + xs[i][6] * co[7] + xs[i][7] * co[8]
		yp += xs[i][8] * co[9] + xs[i][9] * co[10] + xs[i][10] * co[11]
		yps.append(yp)
	
	ts = range(len(xs))
	plt.plot(ts, ys, 'o', label='Original data', linestyle='-', marker='')
	plt.plot(ts, yps, 'r', label='Fitted line')
	plt.legend()
	plt.show()
			
		
def slope(datas):
	l = len(datas)
	xs = np.arange(l)
	xsT = np.array([xs, np.ones(l)]).T
	m, c = np.linalg.lstsq(xsT, datas)[0]
	return m
	
def std(datas):
	return np.std(datas, dtype=np.float64, ddof=0)
	
def findData(dtlong, datas, ds, length=10):
	l = len(datas)
	for i in range(length-1, l):
		datadtlong = datas[i]['dtlong']
		if datadtlong == dtlong:
			return ds[i-length+1 : i+1]
		elif datadtlong > dtlong:
			#log.debug('Cannot find for: ' + str(dtlong))
			return None
	#log.debug('Cannot find for: ' + str(dtlong))
	return None
	

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
	clearLog()
	co = regression()
	#co = [4.45976373e-03,9.99751491e-01,-2.11500584e-02,2.04798247e-02,-2.28103878e-02,-3.51360548e-03,4.18686572e-03,-8.30510546e-05,-2.37747656e-04,-4.77724273e-05,-3.57309769e-04,5.80726971e-04]
	#testCo(co)
	