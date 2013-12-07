# -*- coding: utf-8 -*-
import urllib2 
import re
from utils.rwlogging import log

def smsSelf(msg):
	sms(msg, '13811830642')
	
def smsFamily(msg):
	sms(msg, '13811830642')
	sms(msg, '13810536149')
	sms(msg, '13693718965')
	
def sms(msg, receiver):
	url = 'https://quanapi.sinaapp.com/fetion.php?u=13811830642&p='
	url = url + '&to=' + urllib2.quote(receiver)
	url = url + '&m=' + urllib2.quote(msg.encode('utf-8'))
	ret = urllib2.urlopen(url).read()
	#ret = '00000'
	log.info('receiver ' + receiver + 'Sending ' + msg + ', result: ' + ret)
