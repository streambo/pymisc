# -*- coding: utf-8 -*-

db = SqliteDB()

def monitor():
	msg = ''
	#Agg
	try:
		aggPrice = fetchAgg()
		msg = msg + monitorPrice('AGG', aggPrice)
	except:
		traceback.print_exc()
	
	if msg:
		sendmessage(msg)

def monitorPrice(ptype, price):
	ret = ''
	
	dLong = time.mktime(price['dt'].timetuple())
	dDate = price['dt'].strftime('%Y-%m-%d')
	dTime = price['dt'].strftime('%H:%M:%S')
	
	db.addPrice((ptype, dLong, dDate, dTime, price['p'], '', dLong, dDate, dTime))
	
	# get the price of 30 minutes ago
	price30 = db.getPrice(ptype, dLong - 1800)
	
	# calculate the percentage
	percent0 = price['per']
	percent30 = abs((price - price30) / price30)
	
	# get last message information
	notper0 = db.getNotice(ptype, 0, dDate)
	if abs(percent0 - notper0) >= 1:
		ret = ptype + '0,' + price + ',' + percent0 + '%\n'
		db.updateNotice((ptype, 0, dLong, dDate, dTime, price['p'], percent0, ret, ''))
	
	notcount30 = db.getNoticeCount(ptype, 30, dLong - 1800)
	if notcount30 == 0 and percent30 >= 1:
		ret = ret + ptype + '30,' + price + ',' + percent30 + '%\n'
		db.updateNotice((ptype, 30, dLong, dDate, dTime, price['p'], percent30, ret, ''))
	
	return ret;
	

def sinaAgg():
	# fetch price of London
	f = urllib2.urlopen('http://hq.sinajs.cn/?_=1386077085140/&list=hf_XAG')
	html = f.read()
	html = html[19:len(html) - 2]
	xagArr = re.split(',', html)
	
	price = {}
	price['dt'] = datetime.datetime.strptime(xagArr[13] + ' ' + xagArr[6], '%Y-%m-%d %H:%M:%S')
	xag = float(xagArr[0])
	xag0 = float(xagArr[2])
	
	# fetch USD price
	fusd = urllib2.urlopen('http://hq.sinajs.cn/rn=13860770561347070422433316708&list=USDCNY')
	htmlusd = fusd.read()
	htmlusd = htmlusd[19:len(htmlusd) - 2]
	usdArr = re.split(',', htmlusd)
	usd = float(usdArr[0])
	
	# calculate price in RMB
	price['p'] = usd * xag / 31.1035
	price['p0'] = usd * xag0 / 31.1035
	price['per'] = float(xagArr[1])
	return price
	
def icbcAgg():
	f = urllib2.urlopen('http://www.icbc.com.cn/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx', timeout=60)
	html = f.read()
	silverRmbPattern = re.compile(r"""人民币账户白银\s*</td>\s*<td[\s\S]+?</td>\s*<td.*?>\s*(.*?)\s*</td>
\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>""", re.S + re.X)
	pmsSilverRmb = silverRmbPattern.search(html)
	
	# Date Time
	price['dt'] = datetime.datetime.now()
	price['p'] = float(pmsSilverRmb.group(3))
	high = float(pmsSilverRmb.group(4))
	low = float(pmsSilverRmb.group(5))
	if high - price['p'] > price['p'] - low:
		price['p0'] = high
		price['per'] = abs((price['p'] - high) / high)
	else:
		price['p0'] = low
		price['per'] = abs((price['p'] - low) / low)
		
	return price
	
	
