# -*- coding: utf-8 -*-
import threading
from apscheduler.scheduler import Scheduler
from utils.db import SqliteDB
from utils.rwlogging import log
from notifier import fetion
from notifier import mail
from category import prices
from category import weather

def minuteMonitor():
	# Investments 
	try:
		msg = ''
		msg = msg + prices.monitorPrice()
		# sending message if available
		if msg:
			log.info('* minuteMonitor MESSAGE * ' + msg)
			sendMessage('Prices', msg, 1)
	except:
		log.exception('minuteMonitor Exception Occured!')

def marketMonitor():
	# Investments 
	try:
		msg = ''
		msg = msg + prices.latestPrices()
		# sending message if available
		if msg:
			log.info('* marketMonitor MESSAGE * ' + msg)
			sendMessage('Market', msg, 1)
	except:
		log.exception('marketMonitor Exception Occured!')

def weatherMonitor():
	try:
		msg = ''
		msg = msg + weather.fetchWeather()
		# sending message if available
		if msg:
			log.info('* weatherMonitor MESSAGE * ' + msg)
			sendMessage('Weather', msg, 2)
	except:
		log.exception('weatherMonitor Exception Occured!')

def pm25Monitor():
	try:
		msg = ''
		msg = msg + weather.fetchPm25Forcast()
		if msg:
			log.info('* pm25Monitor MESSAGE * ' + msg)
			sendMessage('PM2.5', msg, 2)
	except:
		log.exception('pm25Monitor Exception Occured!')
	
def sendMessage(mtype, msg, rtype):
	try:
		mail.send(mtype, msg)
	except:
		log.exception('Email Exception Occured!')
		
	try:
		if rtype == 1:
			fetion.smsSelf(msg)
		else:
			fetion.smsFamily(msg)
	except:
		log.exception('Fetion Exception Occured!')
		
	
def batchMonitor():
	try:
		db = SqliteDB()
		db.cleanOldData()
	except:
		log.exception('dayMonitor Exception Occured!')

def process(func):
	thread = threading.Thread(target=func)
	thread.start()
	thread.join(120)
	if thread.is_alive():
		log.info('* hanging thread * ')
	else:
		log.debug('* thread ended normally * ')
		
if __name__ == "__main__":
	sched = Scheduler(standalone=True)
	#sched.add_cron_job(minuteMonitor, day_of_week='mon', hour='7-23', minute='*')
	#sched.add_cron_job(minuteMonitor, day_of_week='tue-fri', minute='*')
	#sched.add_cron_job(minuteMonitor, day_of_week='sat', hour='0-3', minute='*')
	sched.add_cron_job(process, args=[minuteMonitor], day_of_week='mon', hour='7-23', minute='*')
	sched.add_cron_job(process, args=[minuteMonitor], day_of_week='tue-fri', second='0,30')
	sched.add_cron_job(process, args=[minuteMonitor], day_of_week='sat', hour='0-3', minute='*')
	sched.add_cron_job(process, args=[weatherMonitor], hour='7', minute='30')
	sched.add_cron_job(process, args=[weatherMonitor], hour='17,21', minute='0')
	sched.add_cron_job(process, args=[pm25Monitor], hour='19', minute='0')
	sched.add_cron_job(process, args=[marketMonitor], day_of_week='mon-fri', hour='11,15,21', minute='15')
	sched.add_cron_job(process, args=[batchMonitor], hour='1', minute='0')
	log.info('Monitor starting...')
	sched.start()
