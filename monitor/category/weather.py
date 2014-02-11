# -*- coding: utf-8 -*-
import urllib2, StringIO, gzip
import json
import datetime
from utils.rwlogging import log

dictwe = {'00':u'晴','001':u'晴','01':u'多云','011':u'多云','02':u'阴',
'03':u'阵雨','04':u'雷阵雨','05':u'雷阵雨伴有冰雹','06':u'雨夹雪','07':u'小雨',
'08':u'中雨','09':u'大雨','10':u'暴雨','11':u'大暴雨','12':u'特大暴雨',
'13':u'阵雪','14':u'小雪','15':u'中雪','16':u'大雪','17':u'暴雪',
'18':u'雾','19':u'冻雨','20':u'沙尘暴','21':u'小到中雨','22':u'中到大雨',
'23':u'大到暴雨','24':u'暴雨到大暴雨','25':u'大暴雨到特大暴雨','26':u'小到中雪',
'27':u'中到大雪','28':u'大到暴雪','29':u'浮尘','30':u'扬沙','31':u'强沙尘暴','53':u'霾','99':u'无'}

dictwo = {'0':'', '1':u'东北风', '2':u'东风', '3':u'东南风',
'4':u'南风', '5':u'西南风', '6':u'西风', '7':u'西北风', '8':u'北风', '9':u'旋转风'}

dictws = {'0':u'微风', '1':u'3-4级', '2':u'4-5级', '3':u'5-6级', '4':u'6-7级',
'5':u'7-8级', '6':u'8-9级', '7':u'9-10级', '8':u'10-11级', '9':u'11-12级'}

def fetchWeather(city):
	req = urllib2.Request('http://ext.weather.com.cn/' + city + '.json')
	req.add_header('Referer', 'http://ext.weather.com.cn/p.html')
	resp = urllib2.urlopen(req, timeout=20)
	if resp.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(resp.read())
		f = gzip.GzipFile(fileobj=buf)
		retjson = f.read()
	else:
		retjson = resp.read()
	climate = json.loads(retjson)
	
	req = urllib2.Request('http://mobile.weather.com.cn/data/forecast/' + city + '.html?_=1386498530227')
	req.add_header('Referer', 'http://mobile.weather.com.cn/weather/' + city + '.html')
	resp = urllib2.urlopen(req, timeout=20)
	if resp.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(resp.read())
		f = gzip.GzipFile(fileobj=buf)
		retjson = f.read()
	else:
		retjson = resp.read()
	forcast = json.loads(retjson)
	
	dt = datetime.datetime.now().strftime('%H:%M')
	msg = climate['n'] + ',' + dt + ',' + climate['s'] + ',' + climate['t'] + u'℃,' + climate['w'] + u',湿度' + str(climate['h']) + '%;\n'
	
	if city == '101010200':
		msg = msg + fetchBJpm25()
	elif city == '101180101':
		msg = msg + fetchZZpm25()
	
	if forcast['f']['f1'][0]['fa']:
		msg = msg + u'今天白天:' + dictwe[forcast['f']['f1'][0]['fa']]
		msg = msg + u',最高' + forcast['f']['f1'][0]['fc'] + u'℃,'
		msg = msg + dictwo[forcast['f']['f1'][0]['fe']] + dictws[forcast['f']['f1'][0]['fg']] + '\n'
	msg = msg + u'今天晚间:' + dictwe[forcast['f']['f1'][0]['fb']]
	msg = msg + u',最低' + forcast['f']['f1'][0]['fd'] + u'℃,'
	msg = msg + dictwo[forcast['f']['f1'][0]['ff']] + dictws[forcast['f']['f1'][0]['fh']] + '\n'
	msg = msg + u'明天白天:' + dictwe[forcast['f']['f1'][1]['fa']]
	msg = msg + u',最高' + forcast['f']['f1'][1]['fc'] + u'℃,'
	msg = msg + dictwo[forcast['f']['f1'][1]['fe']] + dictws[forcast['f']['f1'][1]['fg']]
	return msg

def fetchBJpm25():
	try:
		resp = urllib2.urlopen('http://zx.bjmemc.com.cn/ashx/Data.ashx?Action=GetAQIClose1h', timeout=20)
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
		
		return u'空气指数:' + wlpm25['AQIValue'] + ',' + wlpm25['Quality'] + '\n'
	except:
		log.exception('fetchBJpm25 Exception Occured!')
		return ''

def fetchZZpm25():
	try:
		dt = datetime.datetime.now().strftime('%Y-%m-%d')
		dhour = datetime.datetime.now().hour
		dhour = dhour - 1
		
		url = 'http://www.zzemc.cn/em_aw/Services/DataCenter.aspx?type=getPointHourData&code=2&time='
		url = url + dt + '%20' + str(dhour) + ':00:00'
		#log.debug(url)
		resp = urllib2.urlopen(url, timeout=20)
		ac = json.loads(resp.read())
		ac = ac['Head'][0]
		pm25 = int(float(ac['PM25']) * 1000)
		
		return u'空气指数: ' + str(pm25) + '\n'
	except:
		log.exception('fetchZZpm25 Exception Occured!')
		return ''
	
def fetchPm25Forcast():
	resp = urllib2.urlopen('http://zx.bjmemc.com.cn/ashx/DayForecast.ashx', timeout=20)
	if resp.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(resp.read())
		f = gzip.GzipFile(fileobj=buf)
		retjson = f.read()
	else:
		retjson = resp.read()
	pm25 = json.loads(retjson)[0]
	
	msg = u'PM2.5预报:今晚'
	if pm25['QualityN']:
		msg = msg + pm25['QualityN']
	else:
		msg = msg + u'无'
	if pm25['AQIN']:
		msg = msg + pm25['AQIN']
	if pm25['DescriptionN']:
		msg = msg + '\n' + pm25['DescriptionN']
		
	msg = msg + u'\n明天'
	if pm25['QualityD']:
		msg = msg + pm25['QualityD']
	else:
		msg = msg + u'无'
	if pm25['AQID']:
		msg = msg + pm25['AQID']
	if pm25['DescriptionD']:
		msg = msg + '\n' + pm25['DescriptionD']
	return msg

