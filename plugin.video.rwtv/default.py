# -*- coding: utf-8 -*-
import urllib2, urllib, StringIO, gzip
import xbmc, xbmcgui, xbmcaddon, xbmcplugin

if sys.version_info < (2, 7):
	import simplejson
else:
	import json as simplejson
	
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo("name")

def log(txt):
	message = "%s: %s" % (__addonname__, unicode(txt).encode('utf-8'))
	print(message)

def genPluginUrl(mode, params):
	pluginName = sys.argv[0]
	paramUrl = 'mode=' + mode
	for key, value in params.iteritems():
		paramUrl = paramUrl + '&' + key + '=' + urllib.quote_plus(value.encode('utf8'))
	#log(pluginName + "?" + paramUrl)
	return pluginName + "?" + paramUrl

def rootList():
	windowId = int(sys.argv[1])
	item = xbmcgui.ListItem('电视')
	url = genPluginUrl('list', {"mtype": "TV"})
	xbmcplugin.addDirectoryItem(windowId, url, item, True)
	item = xbmcgui.ListItem('电台')
	url = genPluginUrl('list', {"mtype": "RADIO"})
	xbmcplugin.addDirectoryItem(windowId, url, item, True)
	xbmcplugin.endOfDirectory(windowId)

def progList(mtype):
	windowId = int(sys.argv[1])
	resp = urllib2.urlopen('http://roland.duapp.com/xbmc/list.json?ctype=' + mtype)
	html = resp.read()
	#log(html[:50])
	datas = simplejson.loads(html)
	for data in datas:
		item = xbmcgui.ListItem(data['title'], thumbnailImage=data['icon'])
		item.setInfo(type=data['type'], infoLabels={"Title":data['title']})
		url = genPluginUrl('play', {"mediaUrl":data['url'], 'iconUrl':data['icon'], 'mediaName':data['title'], 'mediaType':data['type']})
		#print data['url']
		xbmcplugin.addDirectoryItem(windowId, url, item, False)
	xbmcplugin.endOfDirectory(windowId)

def playProg(mediaUrl, iconUrl, mediaName, mediaType):
	item = xbmcgui.ListItem(mediaName, thumbnailImage=iconUrl)
	item.setInfo(type=mediaType, infoLabels={"Title": mediaName})
	xbmc.Player().play(mediaUrl, item)

def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?', '')
		if (params[len(params) - 1] == '/'):
			params = params[0:len(params) - 2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]
	return param

params=get_params()

mode=None
mtype=None
mediaUrl=None
iconUrl=None
mediaName=None
mediaType=None

try:
	mode = params["mode"]
except:
	pass

try:
	mtype = urllib.unquote_plus(params["mtype"])
except:
	pass

try:
	mediaUrl = urllib.unquote_plus(params["mediaUrl"]).decode('utf8')
except:
	pass

try:
	iconUrl = urllib.unquote_plus(params["iconUrl"]).decode('utf8')
except:
	pass

try:
	mediaName = urllib.unquote_plus(params["mediaName"]).decode('utf8')
except:
	pass

try:
	mediaType = params["mediaType"]
except:
	pass

#log('mode=' + str(mode) + ',mtype=' + str(mtype) + ',mediaName=' + str(mediaName) + ',mediaUrl=' + str(mediaUrl) + ',iconUrl=' + str(iconUrl) + ',mediaType=' + str(mediaType))
log('mode=' + str(mode) + ',mtype=' + str(mtype) + ',mediaUrl=' + str(mediaUrl) + ',iconUrl=' + str(iconUrl) + ',mediaType=' + str(mediaType))

if mode == None:
	rootList()
elif mode == 'list':
	progList(mtype)
elif mode == 'play':
	playProg(mediaUrl, iconUrl, mediaName, mediaType)
