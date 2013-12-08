# -*- coding: utf-8 -*-
import urllib2, StringIO, gzip
import json
import datetime
from utils.rwlogging import log

def fetchWeather():
	req = urllib2.Request('http://ext.weather.com.cn/101010200.json')
	req.add_header('Referer', 'http://ext.weather.com.cn/p.html')
	resp = urllib2.urlopen(req, timeout=2)
	if resp.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(resp.read())
		f = gzip.GzipFile(fileobj=buf)
		retjson = f.read()
	else:
		retjson = resp.read()
	climate = json.loads(retjson)
	
	try:
		resp = urllib2.urlopen('http://m.weather.com.cn/data/101010200.html', timeout=2)
		if resp.info().get('Content-Encoding') == 'gzip':
			buf = StringIO.StringIO(resp.read())
			f = gzip.GzipFile(fileobj=buf)
			retjson = f.read()
		else:
			retjson = resp.read()
		forcast = json.loads(retjson)['weatherinfo']
	except:
		log.exception('m.weather Exception Occured!')
		forcast = {}
		forcast['wind2'] = ''
	
	resp = urllib2.urlopen('http://zx.bjmemc.com.cn/ashx/Data.ashx?Action=GetAQIClose1h', timeout=2)
	if resp.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(resp.read())
		f = gzip.GzipFile(fileobj=buf)
		retjson = f.read()
	else:
		retjson = resp.read()
	pm25s = json.loads(retjson)
	
	wlpm25 = ''
	for pm25 in pm25s:
		if (pm25['StationName'] == u'万柳'): wlpm25 = pm25
	if not wlpm25:
		wlpm25 = pm25s[0]
	
	dt = datetime.datetime.now().strftime('%H:%M')
	msg = climate['n'] + ',' + dt + ',' + climate['s'] + ',' + climate['t'] + unicode('℃,', 'utf-8') + climate['w'] + unicode(',湿度', 'utf-8') + str(climate['h']) + '%;\n'
	msg = msg + unicode('空气指数:', 'utf-8') + wlpm25['AQIValue'] + ',' + wlpm25['Quality'] + ';\n'
	msg = msg + unicode('预报:', 'utf-8') + climate['d2']['s'] + ',' + climate['d1']['l'] + '~' + climate['d2']['h'] + unicode('℃,', 'utf-8') + forcast['wind2']
	return msg

def fetchPm25Forcast():
	resp = urllib2.urlopen('http://zx.bjmemc.com.cn/ashx/DayForecast.ashx', timeout=60)
	if resp.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(resp.read())
		f = gzip.GzipFile(fileobj=buf)
		retjson = f.read()
	else:
		retjson = resp.read()
	pm25 = json.loads(retjson)[0]
	
	msg = unicode('PM2.5预报:今晚', 'utf-8') + pm25['QualityN'] + pm25['AQIN'] + '\n' + pm25['DescriptionN']
	msg = msg + unicode('\n明天', 'utf-8') + pm25['QualityD'] + pm25['AQID'] + '\n' + pm25['DescriptionD']
	return msg


