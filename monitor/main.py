# -*- coding: utf-8 -*-
from apscheduler.scheduler import Scheduler
from utils.db import SqliteDB
from utils.rwlogging import log
from notifier import fetion
from category import prices
from category import weather

def minuteMonitor():
	msg = ''
	# Investments 
	try:
		msg = msg + prices.monitorPrice()
	except:
		log.exception('minuteMonitor Exception Occured!')
	# sending message if available
	if msg:
		log.info('* minuteMonitor MESSAGE * ' + msg)
		fetion.smsSelf(msg)

def marketMonitor():
	msg = ''
	# Investments 
	try:
		msg = msg + prices.latestPrices()
	except:
		log.exception('marketMonitor Exception Occured!')
	# sending message if available
	if msg:
		log.info('* marketMonitor MESSAGE * ' + msg)
		fetion.smsSelf(msg)

def weatherMonitor():
	msg = ''
	try:
		msg = msg + weather.fetchWeather()
	except:
		log.exception('weatherMonitor Exception Occured!')
	# sending message if available
	if msg:
		log.info('* weatherMonitor MESSAGE * ' + msg)
		fetion.smsFamily(msg)

def batchMonitor():
	try:
		db = SqliteDB()
		db.cleanOldData()
	except:
		log.exception('dayMonitor Exception Occured!')
		
if __name__ == "__main__":
	sched = Scheduler(standalone=True)
	#sched.daemonic = False
	#sched.add_cron_job(weatherMonitor, day_of_week='mon-sat', minute='*')
	sched.add_cron_job(minuteMonitor, day_of_week='mon-sat', minute='*')
	sched.add_cron_job(weatherMonitor, hour='7,17,21', minute='0')
	sched.add_cron_job(marketMonitor, day_of_week='mon-fri', hour='11,15,21', minute='15')
	log.info('Monitor starting...')
	sched.start()
