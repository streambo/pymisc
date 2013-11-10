# coding=UTF-8

import urllib2
import re
import datetime
import time
import math
from dbop import FDatabase

def dji():
    f = urllib2.urlopen('http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinlineNService.getMinline?symbol=.dji&day=5&?=0.4058946408331394')
    html = f.read()
    html = html[14:len(html) - 3]
    # Date Time
    fetchdtLong = long(time.time())
    fetchdate = datetime.datetime.now().strftime('%Y-%m-%d')
    fetchtime = datetime.datetime.now().strftime('%H:%M:%S')
    fdb = FDatabase()
    dayArr = re.split(' ', html)
    for dayStr in dayArr:
        sdate = dayStr[0:10]
        #print sdate
        for minStr in re.split(';', dayStr[12:]):
            minArr = re.split(',', minStr)
            dtime = minArr[0]
            ddt = datetime.datetime.strptime(sdate + ' ' + dtime, '%Y-%m-%d %H:%M:%S')
            dlong = time.mktime(ddt.timetuple()) + 12 * 60 * 60
            ddt = datetime.datetime.fromtimestamp(dlong)
            ddate = ddt.strftime('%Y-%m-%d')
            dtime = ddt.strftime('%H:%M:%S')
            #print ddate + ' ' + dtime + ' ' + minArr[3]
            fdb.addData('USADJI', (dlong, ddate, dtime, minArr[3], '', fetchdtLong, fetchdate, fetchtime))
    fdb.commit()
    print 'Importing DJI from sina done!'    
