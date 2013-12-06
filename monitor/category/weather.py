# -*- coding: utf-8 -*-
import urllib2, StringIO, gzip
import json
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
	data = json.loads(retjson)
	msg = data['n'] + ',' + data['s'] + ',' + data['t'] + unicode('℃,', 'utf-8') + data['w'] + ',' + str(data['h']) + '%; '
	msg = msg + unicode('24小时:', 'utf-8') + data['d1']['s'] + ',' + data['d1']['l'] + '~' + data['d1']['h'] + unicode('℃,', 'utf-8') + data['w']
	return msg
