# -*- coding: utf-8 -*-
import urllib2
import re
import datetime
import time
import traceback
from apscheduler.scheduler import Scheduler
from db import SqliteDB
from rwlogging import log
import fetion

db = SqliteDB()
log.debug('moniter launched!')

def monitor():
	msg = ''
	#Agg
	try:
		#aggPrice = icbcAgg()
		aggPrice = sinaAgg()
		msg = msg + monitorPrice('AGG', aggPrice)
	except:
		log.exception('Exception Occured!')
	
	if msg:
		log.info('* MESSAGE * ' + msg)
		fetion.sms(msg)

def monitorPrice(ptype, price):
	ret = ''
	
	dLong = time.mktime(price['dt'].timetuple())
	dDate = price['dt'].strftime('%Y-%m-%d')
	dTime = price['dt'].strftime('%H:%M:%S')
	
	db.addPrice((ptype, dLong, dDate, dTime, price['p'], '', dLong, dDate, dTime))
	
	# calculate the percentage
	percent0 = price['per']
	
	# get the price of 30 minutes ago
	price30 = db.getPrice(ptype, dLong - 1800)
	percent30 = 0
	if price30:
		percent30 = round(abs((price['p'] - price30) / price30) * 100, 3)
	
	# get last message information
	notper0 = db.getNotice(ptype, 0, dDate)
	log.info(ptype + ', percentage 0: ' + str(percent0) + ', last notice: ' + str(notper0))
	#print notper0
	if abs(percent0 - notper0) >= 1:
		ret = ptype + '0,' + str(price['p']) + ',' + str(percent0) + '%\n'
		db.updateNotice((ptype, 0, dLong, dDate, dTime, price['p'], percent0, ret, ''))
	
	notcount30 = db.getNoticeCount(ptype, 30, dLong - 1800)
	log.info(ptype + ', percentage 30: ' + str(percent30) + ', notice in 30 minutes: ' + str(notcount30))
	if notcount30 == 0 and percent30 >= 1:
		ret = ret + ptype + '30,' + str(price['p']) + ',' + str(percent30) + '%\n'
		db.updateNotice((ptype, 30, dLong, dDate, dTime, price['p'], percent30, ret, ''))
	
	return ret;
	

def sinaAgg():
	# fetch price of London
	f = urllib2.urlopen('http://hq.sinajs.cn/?_=1386077085140/&list=hf_XAG')
	html = f.read()
	html = html[19:len(html) - 3]
	xagArr = re.split(',', html)
	
	price = {}
	price['dt'] = datetime.datetime.strptime(xagArr[12] + ' ' + xagArr[6], '%Y-%m-%d %H:%M:%S')
	xag = float(xagArr[0])
	xag0 = float(xagArr[7])
	log.debug('XAG: ' + xagArr[0] + ', XAG0: ' + xagArr[2])
	
	# fetch USD price
	fusd = urllib2.urlopen('http://hq.sinajs.cn/rn=13860770561347070422433316708&list=USDCNY')
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
	
def icbcAgg():
	f = urllib2.urlopen('http://www.icbc.com.cn/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx', timeout=60)
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
		price['per'] = round(abs((price['p'] - high) / high) * 100, 3)
	else:
		price['p0'] = low
		price['per'] = round(abs((price['p'] - low) / low) * 100, 3)
		
	log.info('icbc agg: ' + str(price['dt']) + ', ' + str(price['p']) + ', ' + str(price['p0']) + ', ' + str(price['per']))
	return price
	

if __name__ == "__main__":
	sched = Scheduler()
	sched.daemonic = False
	#sched.add_interval_job(monitor, seconds=60) 
	sched.add_cron_job(monitor, day_of_week='mon-sat', minute='*')
	sched.start()
	#monitor()
	
