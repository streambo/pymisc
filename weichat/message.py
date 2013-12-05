#-*- coding:utf-8 -*-
import urllib
import urllib2
import cookielib
import json

cj=cookielib.LWPCookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

#登陆
paras={'username':'rolandwz@qq.com','pwd':'819cf1304065c4ae95f2babaf8a03fd7','imgcode':'','f':'json'}
req=urllib2.Request('https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN',urllib.urlencode(paras))
req.add_header('Accept','application/json, text/javascript, */*; q=0.01')
req.add_header('Accept-Encoding','gzip,deflate,sdch')
req.add_header('Accept-Language','zh-CN,zh;q=0.8')
req.add_header('Connection','keep-alive')
req.add_header('Content-Length','79')
req.add_header('Content-Type','application/x-www-form-urlencoded; charset=UTF-8')
req.add_header('Host','mp.weixin.qq.com')
req.add_header('Origin','https://mp.weixin.qq.com')
req.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN')
req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36')
req.add_header('X-Requested-With','XMLHttpRequest')
ret=urllib2.urlopen(req)
retread=ret.read()
print retread
token=json.loads(retread)

#print token['ErrMsg'][44:]
token=token['ErrMsg'][44:] 
print token
#接下就可以推送消息了。
#进入用户管理，点击你要发送消息的用户，使用同样办法，找到请求 singlesend?t=ajax-response&lang=zh_CN ，得到请求头和post的数据。
#推送消息的代码如下：

paras2={'type':'1','content':'Hello, Roland','error':'false','imgcode':'','tofakeid':'523485','token':token,'ajax':'1'}# content为你推送的信息，tofakeid为用户的唯一标示id，可在html代码里找到
req2=urllib2.Request('https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&lang=zh_CN',urllib.urlencode(paras2))
req2.add_header('Accept','*/*')
req2.add_header('Accept-Encoding','gzip,deflate,sdch')
req2.add_header('Accept-Language','zh-CN,zh;q=0.8')
req2.add_header('Connection','keep-alive')
#req2.add_header('Content-Length','77')  此行代码处理发送数据长度的确认，不要加。是个坑。
req2.add_header('Content-Type','application/x-www-form-urlencoded; charset=UTF-8')
req2.add_header('Host','mp.weixin.qq.com')
req2.add_header('Origin','https://mp.weixin.qq.com')
req2.add_header('Referer','https://mp.weixin.qq.com/cgi-bin/singlemsgpage?msgid=&source=&count=20&t=wxm-singlechat&fromfakeid=150890&token=%s&lang=zh_CN'%token)
req2.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36')
req2.add_header('X-Requested-With','XMLHttpRequest')
#不加cookie也可发送
#req2.add_header('Cookie',cookie2)
ret2=urllib2.urlopen(req2)
#ret2=opener.open(req2)
print 'x',ret2.read()