# -*- coding: utf-8 -*-
import urllib2
import json
from utils.rwlogging import log

def fetchWeather():
	f = urllib2.urlopen('http://ext.weather.com.cn/101010200.json')
	html = f.read()
	#html = '{"l":"冬月初三","c":"101010200","n":"海淀","en":"haidian","t":"3","w":"西南风 1级","h":48,"s":"晴","d1":{"l":"-3","h":"13","s":"晴","w":"无持续风向"},"d2":{"l":"-3","h":"11","s":"晴"},"d3":{"l":"-1","h":"12","s":"晴"},"w1":"无持续风向","i":{"cityid":"101010200","cy":{"level":null,"label":"冷","description":"天气冷，建议着棉服、羽绒服、皮夹克加羊毛衫等冬季服装。年老体弱者宜着厚棉衣、冬大衣或厚羽绒服。"},"xc":{"level":null,"label":"适宜","description":"适宜洗车，未来持续两天无雨天气较好，适合擦洗汽车，蓝天白云、风和日丽将伴您的车子连日洁净。"},"uv":{"level":null,"label":"中等","description":"属中等强度紫外线辐射天气，外出时建议涂擦SPF高于15、PA+的防晒护肤品，戴帽子、太阳镜。"},"aq":{"level":"24,7,9","label":"优","description":"可多参加户外活动呼吸新鲜空气"},"pl":{"level":null,"label":"中","description":"气象条件对空气污染物稀释、扩散和清除无明显影响，易感人群应适当减少室外活动时间。"}}}'
	data = json.loads(html)
	msg = data['n'] + ',' + data['s'] + ',' + data['t'] + unicode('℃,', 'utf-8') + data['w'] + ',' + str(data['h']) + '%,\n'
	msg = msg + unicode('24小时:', 'utf-8') + data['d1']['s'] + ',' + data['d1']['l'] + '~' + data['d1']['h'] + unicode('℃,', 'utf-8') + data['w']
	return msg
