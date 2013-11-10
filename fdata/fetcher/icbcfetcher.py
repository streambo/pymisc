# coding=UTF-8

import urllib2
import re
import datetime
import time
import math
import traceback
from dbop import FDatabase

def silverRmb():
    f = urllib2.urlopen('http://www.icbc.com.cn/ICBCDynamicSite/Charts/TimeLine.aspx?pWidth=1010&pHeight=600&dataType=0&dataId=903&picType=3')
    html = f.read()
    #pattern = re.compile(r"""dataCell\.cell0 = \"(.*?)\";dataCell\.cell1 = \"(.*?)\"""", re.S + re.X)
    pattern = re.compile(r"""dataCell\.cell0\s=\s\"(.*?)\";dataCell\.cell1\s=\s\"(.*?)\";dataCell.cell2\s=\s\"(.*?)\";""", re.S + re.X)
    # Date Time
    fetchdtLong = long(time.time())
    fetchdate = datetime.datetime.now().strftime('%Y-%m-%d')
    fetchtime = datetime.datetime.now().strftime('%H:%M:%S')
    fdb = FDatabase()
    for m in re.finditer(pattern, html):
        #print '%02d-%02d: %s, %s, %s' % (m.start(), m.end(), m.group(1), m.group(2), m.group(3))
        ddt = datetime.datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
        dlong = time.mktime(ddt.timetuple())
        ddate = ddt.strftime('%Y-%m-%d')
        dtime = ddt.strftime('%H:%M:%S')
        fdb.addData('SILVERRMB', (dlong, ddate, dtime, m.group(2), '', fetchdtLong, fetchdate, fetchtime))
    fdb.commit()
    print 'Importing silver rmb from icbc done!'

def goldUsd():
    f = urllib2.urlopen('http://www.icbc.com.cn/ICBCDynamicSite/Charts/TimeLine.aspx?pWidth=1010&pHeight=600&dataType=0&dataId=801&picType=3')
    html = f.read()
    #pattern = re.compile(r"""dataCell\.cell0 = \"(.*?)\";dataCell\.cell1 = \"(.*?)\"""", re.S + re.X)
    pattern = re.compile(r"""dataCell\.cell0\s=\s\"(.*?)\";dataCell\.cell1\s=\s\"(.*?)\";dataCell.cell2\s=\s\"(.*?)\";""", re.S + re.X)
    # Date Time
    fetchdtLong = long(time.time())
    fetchdate = datetime.datetime.now().strftime('%Y-%m-%d')
    fetchtime = datetime.datetime.now().strftime('%H:%M:%S')
    fdb = FDatabase()
    for m in re.finditer(pattern, html):
        #print '%02d-%02d: %s, %s, %s' % (m.start(), m.end(), m.group(1), m.group(2), m.group(3))
        ddt = datetime.datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
        dlong = time.mktime(ddt.timetuple())
        ddate = ddt.strftime('%Y-%m-%d')
        dtime = ddt.strftime('%H:%M:%S')
        fdb.addData('GOLDUSD', (dlong, ddate, dtime, m.group(2), '', fetchdtLong, fetchdate, fetchtime))
    fdb.commit()
    print 'Importing gold usd from icbc done!'

def agTD():
    f = urllib2.urlopen('http://www.icbc.com.cn/ICBCDynamicSite/Charts/TimeLine.aspx?pWidth=1010&pHeight=600&dataType=1&dataId=Ag(T%2BD)&picType=3')
    html = f.read()
    #pattern = re.compile(r"""dataCell\.cell0 = \"(.*?)\";dataCell\.cell1 = \"(.*?)\"""", re.S + re.X)
    pattern = re.compile(r"""dataCell\.cell0\s=\s\"(.*?)\";dataCell\.cell1\s=\s\"(.*?)\";dataCell.cell2\s=\s\"(.*?)\";""", re.S + re.X)
    # Date Time
    fetchdtLong = long(time.time())
    fetchdate = datetime.datetime.now().strftime('%Y-%m-%d')
    fetchtime = datetime.datetime.now().strftime('%H:%M:%S')
    fdb = FDatabase()
    for m in re.finditer(pattern, html):
        #print '%02d-%02d: %s, %s, %s' % (m.start(), m.end(), m.group(1), m.group(2), m.group(3))
        agTddt = datetime.datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S')
        agTdLong = time.mktime(agTddt.timetuple())
        agTdDate = agTddt.strftime('%Y-%m-%d')
        agTdTime = agTddt.strftime('%H:%M:%S')
        fdb.addAgTd((agTdLong, agTdDate, agTdTime, m.group(2), '0', fetchdtLong, fetchdate, fetchtime))
    fdb.commit()
    print 'Importing agtd from icbc done!'


def jobPrecialMental():
    try:
        f = urllib2.urlopen('http://www.icbc.com.cn/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx', timeout=60)
        html = f.read()
        silverRmbPattern = re.compile(r"""人民币账户白银\s*</td>\s*<td[\s\S]+?</td>\s*<td.*?>\s*(.*?)\s*</td>
\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>""", re.S + re.X)
        goldUsdPattern = re.compile(r"""美元账户黄金
\s*</td>\s*<td[\s\S]+?</td>\s*<td.*?>\s*(.*?)\s*</td>
\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>""", re.S + re.X)
        agTDPattern = re.compile(r"""Ag\(T\+D\)
\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td[\s\S]+?</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>
\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>\s*<td.*?>\s*(.*?)\s*</td>
\s*<td.*?>\s*(.*?)\s*</td>""", re.S + re.X)
        pmsSilverRmb = silverRmbPattern.search(html)
        pmsGoldUsd = goldUsdPattern.search(html)
        pmsAgTD = agTDPattern.search(html)
        # Date Time
        fetchdtLong = long(time.time())
        fetchdate = datetime.datetime.now().strftime('%Y-%m-%d')
        fetchtime = datetime.datetime.now().strftime('%H:%M:%S')
        # Ag T+D Date Time
        agTddt = datetime.datetime.strptime(pmsAgTD.group(8), '%Y-%m-%d %H:%M:%S')
        agTdLong = time.mktime(agTddt.timetuple())
        agTdDate = agTddt.strftime('%Y-%m-%d')
        agTdTime = agTddt.strftime('%H:%M:%S')
        print('fetchdt:' + str(fetchdtLong) + ',fetchdate:' + fetchdate + ',fetchtime:' + fetchtime)
        print('SilverRmb:' + pmsSilverRmb.group(3) + ',GoldUsd:' + pmsGoldUsd.group(3))
        print('AgTd:' + pmsAgTD.group(1) + ', Volume:' + pmsAgTD.group(3) + ', Time:' + pmsAgTD.group(8))
        fdb = FDatabase()
        fdb.addData('SILVERRMB', (fetchdtLong, fetchdate, fetchtime, pmsSilverRmb.group(3), '', fetchdtLong, fetchdate, fetchtime))
        fdb.addData('GOLDUSD', (fetchdtLong, fetchdate, fetchtime, pmsGoldUsd.group(3), '', fetchdtLong, fetchdate, fetchtime))
        fdb.addAgTd((agTdLong, agTdDate, agTdTime, pmsAgTD.group(1), pmsAgTD.group(3), fetchdtLong, fetchdate, fetchtime))
        fdb.commit()
    except:
        traceback.print_exc()
