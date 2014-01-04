# -*- coding: utf-8 -*-
import threading
from apscheduler.scheduler import Scheduler
from utils.db import SqliteDB
from utils.rwlogging import log
from notifier import fetion
from notifier import mail
from category import prices
from category import weather
from utils import const

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
		multimsg = [0, 0]
		multimsg[0] = [0, 0]
		multimsg[0][0] = weather.fetchWeather('101010200')
		multimsg[0][1] = const.WEATHER_BJ_MOBILES
		multimsg[1] = [0, 0]
		multimsg[1][0] = weather.fetchWeather('101180101')
		multimsg[1][1] = const.WEATHER_ZZ_MOBILES
		
		sendMultiMessage('Weather', multimsg)
		
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
	
def sendMultiMessage(mtype, multimsg):
	try:
		for msgs in multimsg:
			mail.send(mtype, msgs[0])
	except:
		log.exception('Email Exception Occured!')
		
	try:
		fetion.sendMultiSms(multimsg)
	except:
		log.exception('Fetion Exception Occured!')
		
def sendMessage(mtype, msg, rtype):
	multimsg = []
	multimsg[0] = []
	multimsg[0][0] = msg
	if rtype == 1:
		multimsg[0][1] = const.SELF_MOBILE
	else:
		multimsg[0][1] = const.FAMILY_MOBILES
		
	sendMultiMessage(mtype, multimsg)
	
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
	#sched.add_cron_job(process, args=[minuteMonitor], day_of_week='mon', hour='7-23', minute='*')
	#sched.add_cron_job(process, args=[minuteMonitor], day_of_week='tue-fri', second='0,30')
	#sched.add_cron_job(process, args=[minuteMonitor], day_of_week='sat', hour='0-3', minute='*')
	sched.add_cron_job(process, args=[weatherMonitor], hour='7', minute='30')
	sched.add_cron_job(process, args=[weatherMonitor], hour='17,21', minute='0')
	sched.add_cron_job(process, args=[pm25Monitor], hour='19', minute='0')
	#sched.add_cron_job(process, args=[marketMonitor], day_of_week='mon-fri', hour='11,15,21', minute='15')
	#sched.add_cron_job(process, args=[batchMonitor], hour='1', minute='0')
	log.info('Monitor starting...')
	sched.start()
