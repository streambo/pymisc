# -*- coding: utf-8 -*-
import urllib2, re
from utils.rwlogging import log
from notifier.PyFetion import PyFetion

def smsSelf(msg):
	sendSms(msg, ['13811830642',])
	
def smsFamily(msg):
	#sms(msg, '13810536149')
	#sms(msg, '13811830642')
	#sms(msg, '13693718965')
	receivers = ['13810536149','13811830642','13693718965',]
	sendSms(msg, receivers)
	
def sendSms(msg, receivers):
	try:
		phone = PyFetion.PyFetion('13811830642','','TCP',debug=True)
		if phone.login(PyFetion.FetionOnline):
			log.info('Fetion login success!')
			for receiver in receivers:
				phone.send_sms(msg.encode('utf-8'), receiver, True)
				log.info('SMS sent! receiver ' + receiver + 'Sending ' + msg + '')
			phone.logout()
		else:
			log.info('Fetion login failed, message not send! receivers: ' + receivers + ', msg: ' + msg)
			
	except:
		log.exception('SMS sent failed!')
	
def sms(msg, receiver):
	url = 'https://quanapi.sinaapp.com/fetion.php?u=13811830642&p='
	url = url + '&to=' + urllib2.quote(receiver)
	url = url + '&m=' + urllib2.quote(msg.encode('utf-8'))
	ret = urllib2.urlopen(url).read()
	#ret = '00000'
	log.info('receiver ' + receiver + 'Sending ' + msg + ', result: ' + ret)

	