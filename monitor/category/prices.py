# -*- coding: utf-8 -*-
import urllib2
import re
import datetime
import time
from utils.db import SqliteDB
from utils.rwlogging import log

def monitorPrice():
	msg = ''
	#Agg 
	try:
		#aggPrice = icbcAgg()
		aggPrice = sinaAgg()
		msg = msg + tally('AGG', aggPrice)
	except:
		log.exception('AGG Exception Occured!')
	
	#Agg 
	try:
		agtdPrice = sinaAgTD()
		msg = msg + tally('AGTD', agtdPrice)
		#pass
	except:
		log.exception('AGTD Exception Occured!')
	
	#shdx 
	try:
		shdx = sinaSHDX()
		msg = msg + tally('SHDX', shdx)
		#pass
	except:
		log.exception('SHDX Exception Occured!')
	
	return msg

def latestPrices():
	msg = datetime.datetime.now().strftime('%m-%d %H:%M') + ':\n'
	dtypes = ['AGG', 'AGTD', 'SHDX']
	
	db = SqliteDB()
	dtLong = long(time.time())
	for dtype in dtypes:
		price = db.getPrice(dtype, dtLong)
		msg = msg + dtype + ':' + str(price[0]) + ',' + str(price[1]) + '%,' + str(price[2]) + ';\n'
	
	log.info('latest prices: ' + msg)
	return msg
	
def tally(ptype, price):
	db = SqliteDB()
	ret = ''
	
	dLong = time.mktime(price['dt'].timetuple())
	dDate = price['dt'].strftime('%Y-%m-%d')
	dTime = price['dt'].strftime('%H:%M:%S')
	
	db.addPrice((ptype, dLong, dDate, dTime, price['p'], price['per'], price['p0'], '', dLong, dDate, dTime))
	
	# calculate the percentage
	percent0 = price['per']
	
	# get the price of 30 minutes ago
	price30 = db.getPrice(ptype, dLong - 1800)
	percent30 = 0
	if price30:
		log.debug(ptype + ',price30,' + str(price30[3]) + ',' + str(price30[0]))
		price30 = price30[0]
		percent30 = round((price['p'] - price30) * 100 / price30, 3)
	
	# get last message information
	notper0 = db.getNotice(ptype, 0, dDate)
	log.info(ptype + ', percentage 0: ' + str(percent0) + ', last notice: ' + str(notper0))
	#print notper0
	if abs(percent0 - notper0) >= 1:
		ret = ptype + '0,' + str(price['p']) + ',' + str(percent0) + '%;\n'
		db.addNotice((ptype, 0, dLong, dDate, dTime, price['p'], percent0, ret, ''))
	
	notcount30 = db.getNoticeCount(ptype, 30, dLong - 1800)
	log.info(ptype + ', percentage 30: ' + str(percent30) + ', notice in 30 minutes: ' + str(notcount30))
	if notcount30 == 0 and abs(percent30) >= 1:
		ret = ret + ptype + '30,' + str(price['p']) + ',' + str(percent30) + '%;\n'
		db.addNotice((ptype, 30, dLong, dDate, dTime, price['p'], percent30, ret, ''))
	
	return ret
	

def sinaAgg():
	# fetch price of London
	f = urllib2.urlopen('http://hq.sinajs.cn/?_=1386077085140/&list=hf_XAG', timeout=2)
	html = f.read()
	html = html[19:len(html) - 3]
	xagArr = re.split(',', html)
	
	price = {}
	price['dt'] = datetime.datetime.strptime(xagArr[12] + ' ' + xagArr[6], '%Y-%m-%d %H:%M:%S')
	xag = float(xagArr[0])
	xag0 = float(xagArr[7])
	log.debug('XAG: ' + xagArr[0] + ', XAG0: ' + xagArr[2])
	
	# fetch USD price
	fusd = urllib2.urlopen('http://hq.sinajs.cn/rn=13860770561347070422433316708&list=USDCNY', timeout=2)
	htmlusd = fusd.read()
	htmlusd = htmlusd[19:len(htmlusd) - 3]
	usdArr = re.split(',', htmlusd)
	usd = float(usdArr[1])
	log.debug('USD: ' + usdArr[0])
	
	# calculate price in RMB
	price['p'] = round(usd * xag / 31.1035, 3)
	price['p0'] = round(usd * xag0 / 31.1035, 3)
	price['per'] = float(xagArr[1])
	
	log.info('sina agg: ' + str(price['dt']) + ', ' + str(price['p']) + ', ' + str(price['p0']) + ', ' + str(price['per']))
	return price
	
	
def sinaAgTD():
	# fetch price of AG T+D
	f = urllib2.urlopen('http://hq.sinajs.cn/list=hf_AGTD', timeout=2)
	html = f.read()
	html = html[20:len(html) - 3]
	agtdArr = re.split(',', html)
	
	price = {}
	price['dt'] = datetime.datetime.strptime(agtdArr[12] + ' ' + agtdArr[6], '%Y-%m-%d %H:%M:%S')	
	price['p'] = float(agtdArr[0])
	price['p0'] = float(agtdArr[7])
	price['per'] = round((price['p'] - price['p0']) * 100 / price['p0'], 3)
	
	log.info('sina agtd: ' + str(price['dt']) + ', ' + str(price['p']) + ', ' + str(price['p0']) + ', ' + str(price['per']))
	return price
	
def sinaSHDX():
	# fetch price of AG T+D
	f = urllib2.urlopen('http://hq.sinajs.cn/rn=1386417950746&list=sh000001', timeout=2)
	html = f.read()
	html = html[21:len(html) - 3]
	arr = re.split(',', html)
	
	price = {}
	price['dt'] = datetime.datetime.strptime(arr[30] + ' ' + arr[31], '%Y-%m-%d %H:%M:%S')	
	price['p'] = float(arr[3])
	price['p0'] = float(arr[2])
	price['per'] = round((price['p'] - price['p0']) * 100 / price['p0'], 3)
	
	log.info('sina sh: ' + str(price['dt']) + ', ' + str(price['p']) + ', ' + str(price['p0']) + ', ' + str(price['per']))
	return price
	
def icbcAgg():
	f = urllib2.urlopen('http://www.icbc.com.cn/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx', timeout=2)
	html = f.read()
	silverRmbPattern = re.compile(r"""人民币账户白银\s*</td>\s*<td[\s\S]+?</td>\s*<td.*?>\s*(.*?)\s*</td>
\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>""", re.S + re.X)
	pmsSilverRmb = silverRmbPattern.search(html)
	
	price = {}
	# Date Time
	price['dt'] = datetime.datetime.now()
	price['p'] = float(pmsSilverRmb.group(3))
	high = float(pmsSilverRmb.group(4))
	low = float(pmsSilverRmb.group(5))
	if high - price['p'] > price['p'] - low:
		price['p0'] = high
		price['per'] = round((price['p'] - high) * 100 / high, 3)
	else:
		price['p0'] = low
		price['per'] = round((price['p'] - low) * 100 / low, 3)
		
	log.info('icbc agg: ' + str(price['dt']) + ', ' + str(price['p']) + ', ' + str(price['p0']) + ', ' + str(price['per']))
	return price
	
