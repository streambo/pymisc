# -*- coding: utf-8 -*-
import urllib2, re
from utils.rwlogging import log
from notifier.PyFetion import PyFetion
from utils import const
	
def sendMultiSms(multimsg):
	try:
		phone = PyFetion.PyFetion(const.FETION_USER, const.FETION_PASSWORD, 'TCP', debug=True)
		if phone.login(PyFetion.FetionOnline):
			log.info('Fetion login success!')
			for msgs in multimsg:
				msg = msgs[0]
				for receiver in msgs[1]:
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
	