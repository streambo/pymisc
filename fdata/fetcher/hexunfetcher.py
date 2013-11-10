# coding=UTF-8

import urllib2
import re
import datetime
import time
import math
from xml.dom import minidom
from dbop import FDatabase

def usdx():
    f = urllib2.urlopen('http://quote.forex.hexun.com/ForexXML/MI_CUR5/MI_CUR5_5_usdx.xml?&ts=1376574847490')
    html = f.read()
    root = minidom.parseString(html)
    # Date Time
    fetchdtLong = long(time.time())
    fetchdate = datetime.datetime.now().strftime('%Y-%m-%d')
    fetchtime = datetime.datetime.now().strftime('%H:%M:%S')
    fdb = FDatabase()
    for item in root.getElementsByTagName("Item"):
        usdxPr = item.getElementsByTagName("PR")[0].childNodes[0].nodeValue
        usdxTm = item.getElementsByTagName("ST")[0].childNodes[0].nodeValue
        usdxTm = '2013' + usdxTm + '00'
        # USDX Date Time
        usdxdt = datetime.datetime.strptime(usdxTm, '%Y%m%d%H%M%S')
        usdxLong = time.mktime(usdxdt.timetuple())
        usdxDate = usdxdt.strftime('%Y-%m-%d')
        usdxTime = usdxdt.strftime('%H:%M:%S')
        fdb.addUsdx((usdxLong, usdxDate, usdxTime, usdxPr, '', fetchdtLong, fetchdate, fetchtime))
    fdb.commit()
    print 'Importing USDX from hexun done!'    


