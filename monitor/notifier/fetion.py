# -*- coding: utf-8 -*-
import urllib2, re
from utils.rwlogging import log
from notifier.PyFetion import PyFetion
from utils import const

def smsSelf(msg):
	return sendSms(msg, const.SELF_MOBILE)
	
def smsFamily(msg):
	return sendSms(msg, const.FAMILY_MOBILES)
	
def sendSms(msg, receivers):
	try:
		phone = PyFetion.PyFetion(const.FETION_USER, const.FETION_PASSWORD, 'TCP', debug=True)
		if phone.login(PyFetion.FetionOnline):
			log.info('Fetion login success!')
			for receiver in receivers:
				phone.send_sms(msg.encode('utf-8'), receiver, True)
				log.info('SMS sent! receiver ' + receiver + 'Sending ' + msg + '')
			phone.logout()
			return True
		else:
			log.info('Fetion login failed, message not send! receivers: ' + receivers + ', msg: ' + msg)
			return False
			
	except:
		log.exception('SMS sent failed!')
		return False
	
	