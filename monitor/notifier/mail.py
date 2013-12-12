# -*- coding: utf-8 -*-
import smtplib, re
from email.mime.text import MIMEText
from utils.rwlogging import log
from utils import const

def send(subject, content):
	
	msg = MIMEText(content[28:].encode('utf-8'), 'plain', 'utf-8')
	msg['Subject'] = re.sub('\n', ';', content[:28])
	msg['From'] = const.QQMAIL_ADDR
	msg['To'] = const.QQMAIL_ADDR

	qq = smtplib.SMTP('smtp.qq.com')
	qq.login(const.QQMAIL_USER, const.QQMAIL_PASSWORD)
	ret = qq.sendmail(msg['From'], msg['To'], msg.as_string())
	qq.quit()
	log.info('Sending email: ' + content + '')


