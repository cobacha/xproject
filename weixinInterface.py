# -*- coding: utf-8 -*-
import hashlib
import web
import time
import os
import urllib2,json
import lxml
from lxml import etree
import compute

class WeixinInterface:
    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'template')
        self.render = web.template.render(self.templates_root)
        self.compute = compute.Compute()
    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="duer" #这里改写你在微信公众平台里输入的token
        #字典序排序
        list=[token,timestamp,nonce]
        list.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
    def POST(self):
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        fromUser=xml.find("FromUserName").text
        toUser=xml.find("ToUserName").text
        res,type=self.compute.compute(xml)
        return self.render.reply(fromUser,toUser,int(time.time()),res,type)

class Redirect:
    def __init__(self):
        self.compute = compute.Compute()
    def GET(self):
        data = web.input()
        self.compute.count(data.name.encode('utf-8'))
        return web.redirect(self.compute.get_url(data.name.encode('utf-8')))

class Service:
    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'template')
        self.render = web.template.render(self.templates_root)
        self.compute=compute.Compute()
    def GET(self):
        data=web.input()
        category=data.category.encode('utf-8')
        geo=data.geo.split(',')
        geo=[float(geo[0]),float(geo[1])]
        services=self.compute.find_services(geo, category)
        return self.render.services(services)

