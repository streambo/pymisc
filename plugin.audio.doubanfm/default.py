# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcaddon,  xbmcplugin
import sys, urllib, urlparse, string

if sys.version_info < (2, 7):
	import simplejson
else:
	import json as simplejson

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo("name")

def log(txt):
	message = "%s: %s" % (__addonname__, unicode(txt).encode('utf-8'))
	print(message)
	#xbmc.log(msg = message, level = xbmc.LOGDEBUG)

class DoubanFmPlayer(xbmc.Player):
	def __init__(self):
		xbmc.Player.__init__(self)
		self.channelId = None
		self.songInfos = []
		self.songIds = []
		self.playedSongs = []
		self.playListSize = 1
		self.playing = False
	
	def genPluginUrl(self, params):
		utf8Params = {}
		for key, value in params.iteritems():
			utf8Params[key] = unicode(value).encode('utf-8')
		return self.pluginName + "?" + urllib.urlencode(utf8Params)
	
	def getParam(self, key):
		if self.params.has_key(key):
			return self.params[key]
		else:
			return None
		
	def parseArgv(self, argv):
		print argv
		self.pluginName = argv[0]
		self.windowId = int(argv[1])
		self.params = dict(urlparse.parse_qsl(argv[2][1:]))

		action = self.getParam("action")
		log(action)
		if action == None:
			self.loadChannelList()
		elif action == "playchannel":
			self.channelId = self.getParam("channel_id")
			self.stop()
			xbmc.sleep(1000)
			self.songInfos = []
			self.clearPlayList()
			xbmc.sleep(1000)
			playlist = self.fillPlayList(self.playListSize)
			self.play(playlist)
			self.playing = True
	
	def loadChannelList(self):
		json = urllib.urlopen("http://www.douban.com/j/app/radio/channels").read()
		print json
		data = simplejson.loads(json)
		self.onChannelListLoaded(data["channels"])

	def onChannelListLoaded(self, channelList):
		totalItems = len(channelList)
		for channel in channelList:
			channelName = channel["name"]
			channelId = channel["channel_id"]
			#log("%s - %s" % (channelId, channelName))
			if channelId == '0':
				continue
			item = xbmcgui.ListItem(channelName)
			url = self.genPluginUrl({"action":"playchannel", "channel_id":channelId})
			xbmcplugin.addDirectoryItem(self.windowId, url, item, False, totalItems)
		xbmcplugin.endOfDirectory(self.windowId)
	
	def clearPlayList(self):
		playlist = xbmc.PlayList(0)
		playlist.clear()
		log("play list cleared")
	
	def fillPlayList(self, size):
		playlist = xbmc.PlayList(0)
		for i in range(size):
			song = self.nextSong()
			listItem = xbmcgui.ListItem(song["title"], thumbnailImage=song["picture"])
			listItem.setInfo(type="Music", infoLabels={"Title":song["title"],"Artist":song["artist"],"Album":song["albumtitle"]})
			log("Added to play list: %s - %s" % (song["title"], song["url"]))
			playlist.add(song["url"], listItem)
		return playlist

	def nextSong(self):
		if(len(self.songInfos) <= 0):
			self.songInfos += self.loadSongList(self.channelId)
		return self.songInfos.pop(0)

	def loadSongList(self, channelId):
		log('loadSongList - channelId' + channelId)
		html = urllib.urlopen("http://www.douban.com/j/app/radio/people?app_name=radio_desktop_win&version=100&type=n&channel="+urllib.quote(channelId)).read()
		json = simplejson.loads(html)
		songs = json["song"]
		for song in songs:
			song['picture'] = song['picture'].replace('\\','')
			log("%s - %s(%s)" % (song["title"], song["artist"], song["url"]))
		return songs

	def removePlayedItems(self):
		playlist = xbmc.PlayList(0)
		for song in self.playedSongs:
			playlist.remove(song)
			log("remove played:%s" % song)
		self.playedSongs = []
		return playlist
	
	def setCurrentPlaying(self):
		try:
			self.playedSongs.append(self.getPlayingFile())
			log("%s:[%s]" % ("playedSongs", string.join(self.playedSongs, ",")))
		except:
			log("setCurrentPlaying Error")

	def shouldClose(self):
		return not self.playing

	def onPlayBackEnded(self):
		log("onPlayBackEnded")
		#self.stop()
		#playlist = self.removePlayedItems()
		#self.play(playlist)

	def onPlayBackPaused(self):
		log("onPlayBackPaused")

	def onPlayBackResumed(self):
		log("onPlayBackResumed")

	def onPlayBackSeekChapter(self):
		log("onPlayBackSeekChapter")

	def onPlayBackSpeedChanged(self):
		log("onPlayBackSpeedChanged")

	def onPlayBackStarted(self):
		log("onPlayBackStarted")
		self.playing = True
		self.fillPlayList(1)
		#self.removePlayedItems()
		#self.setCurrentPlaying()

	def onPlayBackStopped(self):
		log("onPlayBackStopped")
		self.clearPlayList()
		self.playing = False

	def onQueueNextItem(self):
		log("onQueueNextItem")


log("addon start")

player = DoubanFmPlayer()
player.parseArgv(sys.argv)

while(not player.shouldClose()):
	xbmc.sleep(1000)

log("addon quit")



