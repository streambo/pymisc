# -*- coding: utf-8 -*-
import urllib2, StringIO, gzip
import json
import datetime
from utils.rwlogging import log

def fetchWeather():
	req = urllib2.Request('http://ext.weather.com.cn/101010200.json')
	req.add_header('Referer', 'http://ext.weather.com.cn/p.html')
	resp = urllib2.urlopen(req)
	if resp.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(resp.read())
		f = gzip.GzipFile(fileobj=buf)
		retjson = f.read()
	else:
		retjson = resp.read()
	climate = json.loads(retjson)
	
	resp = urllib2.urlopen('http://m.weather.com.cn/data/101010200.html')
	if resp.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(resp.read())
		f = gzip.GzipFile(fileobj=buf)
		retjson = f.read()
	else:
		retjson = resp.read()
	forcast = json.loads(retjson)['weatherinfo']
	
	resp = urllib2.urlopen('http://zx.bjmemc.com.cn/ashx/Data.ashx?Action=GetAQIClose1h')
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
	msg = msg + unicode('明天:', 'utf-8') + forcast['weather2'] + ',' + forcast['temp2'] + ',' + forcast['wind2']
	return msg
