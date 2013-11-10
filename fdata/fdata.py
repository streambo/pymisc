# coding=UTF-8
import tornado.ioloop
import tornado.web
import urllib2
import re
import datetime
import time
import math
import json
import os
import numpy
from apscheduler.scheduler import Scheduler
from dbop import FDatabase
from fetcher import icbcfetcher
from fetcher import sinafetcher
from fetcher import hexunfetcher
import traceback

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #sinafetcher.dji()
        self.write("Hello, world")
        
class FetchAllHandler(tornado.web.RequestHandler):
    def get(self):
        hexunfetcher.usdx()
        sinafetcher.dji()
        icbcfetcher.agTD()
        icbcfetcher.silverRmb()
        icbcfetcher.goldUsd()
        self.write("Fetch completed!")

class DatabaseHandler(tornado.web.RequestHandler):
    def get(self):
        fdb = FDatabase()
        op = self.get_argument("op")
        if op == 'empty':
            fdb.emptyTables()
        elif op == 'drop':
            fdb.dropTables()
        elif op == 'create':
            fdb.createTables()
        self.write("Operation Completed: " + op)

def normalize(dataArr, dataName):
    try:
        dispData = {}
        dispData['name'] = dataName
        dispData['points'] = []
        
        if len(dataArr) == 0:
           return dispData 
        vals = []
        for data in dataArr:
            vals.append(data[3])
        avg = numpy.mean(vals)
        stdvar = numpy.std(vals)
        if stdvar == 0:
            diff = 1
        else:
            diff = 100 / stdvar
        #print avg
        #print dataName
        #print stdvar
        #print diff
        dispPoints = []
        for data in dataArr:
            dispVal = {}
            dispVal['x'] = (data[0] + 8 * 60 * 60) * 1000
            dispVal['y'] = (data[3] - avg) * diff
            dispVal['name'] = data[1][5:] + ' ' + data[2]
            dispVal['name'] += ' ' + dataName +  ':<b>' + str(data[3]) + '</b>'
            dispPoints.append(dispVal)
        dispData['points'] = json.dumps(dispPoints)
        return dispData
    except:
        traceback.print_exc()
        dispData = {}
        dispData['name'] = dataName
        dispData['points'] = []
        return dispData
      
class DisplayHandler(tornado.web.RequestHandler):
    def get(self):
        qdate = datetime.datetime.now().strftime('%Y-%m-%d')
        qdate = self.get_argument('qdate', qdate)
        qtime = self.get_argument('qtime', '0')
        qtables = self.get_arguments('qtable', '0')
        # Date Time
        if qtime > 9:
            qdts = qdate + ' ' + str(qtime) + ':00:00'
        else:
            qdts = qdate + ' 0' + str(qtime) + ':00:00'
        print qdts
        qdt = datetime.datetime.strptime(qdts, '%Y-%m-%d %H:%M:%S')
        beginTime = time.mktime(qdt.timetuple())
        endTime = beginTime + 3600
        #print beginTime

        dispSeries = []
        qtablestr = ''
        fdb = FDatabase()
        for qtable in qtables:
            dispSeries.append(normalize(fdb.queryData(qtable, beginTime, endTime), qtable))
            qtablestr += '"' + qtable + '",'

        qtablestr = qtablestr[0:len(qtablestr) - 1]
        #print dispSeries[0]['name']
        # render template
        self.render("template/display.html",
                    qdate=qdate,
                    qtime=qtime,
                    qtables=qtablestr,
                    dispSeries=dispSeries)

def jobFetchAll():
    try:
        hexunfetcher.usdx()
    except:
        traceback.print_exc()
		
    try:
        sinafetcher.dji()
    except:
        traceback.print_exc()
		
    try:
        icbcfetcher.agTD()
    except:
        traceback.print_exc()
		
    try:
        icbcfetcher.silverRmb()
    except:
        traceback.print_exc()
		
    try:
        icbcfetcher.goldUsd()
    except:
        traceback.print_exc()
    print "Fetch completed!"

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/fetch", FetchAllHandler),
    (r"/db", DatabaseHandler),
    (r"/display", DisplayHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'static')}),
])

if __name__ == "__main__":
    sched = Scheduler()
    sched.start()
    #sched.add_interval_job(icbcfetcher.jobPrecialMental, seconds=30) 
    sched.add_cron_job(jobFetchAll, day_of_week='mon-sat', minute=59)
    print('sched started')
    application.listen(88)
    tornado.ioloop.IOLoop.instance().start()
    
