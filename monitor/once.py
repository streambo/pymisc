# -*- coding: utf-8 -*-
import threading, sys
from utils.rwlogging import log
from notifier import fetion
from notifier import mail
from category import prices
from category import weather
from utils import const

def weatherMonitor():
	try:
		#msg = ''
		#msg = msg + weather.fetchWeather()
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
		#for msgs in multimsg:
		#	mail.send(mtype, msgs[0])
		pass
	except:
		log.exception('Email Exception Occured!')
		
	try:
		fetion.sendMultiSms(multimsg)
		pass
	except:
		log.exception('Fetion Exception Occured!')
		
def sendMessage(mtype, msg, rtype):
	multimsg = [0]
	multimsg[0] = [0, 0]
	multimsg[0][0] = msg
	if rtype == 1:
		multimsg[0][1] = const.SELF_MOBILE
	else:
		multimsg[0][1] = const.WEATHER_BJ_MOBILES
		
	sendMultiMessage(mtype, multimsg)
	

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'no arg'
		exit(0)
	arg = sys.argv[1]
	if arg == 'weather':
		weatherMonitor()
	if arg == 'pm25':
		pm25Monitor()
	
