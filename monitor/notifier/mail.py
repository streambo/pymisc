# -*- coding: utf-8 -*-
import smtplib, re
from email.mime.text import MIMEText
from utils.rwlogging import log


def send(subject, content):
	
	msg = MIMEText(content[28:].encode('utf-8'), 'plain', 'utf-8')
	msg['Subject'] = re.sub('\n', ';', content[:28])
	msg['From'] = 'rolandwz@qq.com'
	msg['To'] = 'rolandwz@qq.com'

	qq = smtplib.SMTP('smtp.qq.com')
	qq.login('rolandwz', '')
	ret = qq.sendmail(msg['From'], msg['To'], msg.as_string())
	qq.quit()
	log.info('Sending email: ' + msg + '')


