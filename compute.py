# -*- coding: utf-8 -*-
import sys
import string
import geocoder
import urllib2
import apitools
import duermgr

users={}
class Compute:
    def __init__(self):
        pass

    def compute_content(self, content, user):
        if user not in users or 'geo' not in users[user]:
            return '麻烦您先发送一个地址信息，才能继续为您服务：）','TEXT'

        if '天气' in content and user in users:
            return apitools.GetWeather(users[user]['city'].rstrip('市')),'TEXT'
        else:
            category=duermgr.CheckServiceCategory(content)
            print user
            if user in users and category is not None:
                users[user]['category']=category
            if user in users and 'category' in users[user] and users[user]['category'] is not None:
                res, type=duermgr.Process(users[user], content)
                return res,type
            elif '测试' in content:
                res='<a href="http://m.ayibang.com/appointment/?keyword=project_cleaning&city='+urllib2.quote(users[user]['city'].rstrip('市'))+'">阿姨帮</a>\n'
                res+='<a href="http://m.kuaidi100.com/">快递100</a>'
                return res,'TEXT'
            else:
                return apitools.GetTuringRes(content, user),'TEXT'

    def compute(self, xml):
        user=xml.find('FromUserName').text
        msgType=xml.find('MsgType').text
        if msgType=='text':
            content=xml.find('Content').text.encode('utf-8')
            return self.compute_content(content, user)
        elif msgType=='voice':
            content=xml.find('Recognition').text.encode('utf-8')
            return self.compute_content(content, user)
        elif msgType=='location':
            lat=xml.find('Location_X').text
            lng=xml.find('Location_Y').text
            lng, lat=apitools.GeoConv(lng,lat)
            address, component=geocoder.GetAddress(lat, lng)
            user=xml.find('FromUserName').text
            users.setdefault(user, {})['address']=address.encode('utf-8')
            users.setdefault(user, {})['geo']=[lng,lat]
            users.setdefault(user, {})['city']=component['city'].encode('utf-8')
            return '好的，我记住了:)\n现在你可以给小度发送请求了，目前支持以下内容：\n1、快递\n2、保洁\nbla','TEXT'
        elif msgType=='image':
            image=xml.find('PicUrl').text
            return '图片信息：'+image, 'TEXT'
        elif msgType=='event':
            event=xml.find('Event').text
            if event=='subscribe':
                return '欢迎来到服务通，对我说出你要什么，我就能为你找到身边的服务。例如：我要寄快递、我要搬家、我要保洁、我要找保姆等等。', 'TEXT'
            elif event=='LOCATION':
                lat=xml.find('Latitude').text
                lng=xml.find('Longitude').text
                lng, lat=apitools.GeoConv(lng,lat)
                address, component=geocoder.GetAddress(lat, lng)
                user=xml.find('FromUserName').text
                users.setdefault(user, {})['address']=address.encode('utf-8')
                users.setdefault(user, {})['geo']=[lng, lat]
                users.setdefault(user, {})['city']=component['city'].encode('utf-8')
            else:
                return '对不起，我不能理解你的问题：'+event, 'TEXT'

if __name__=='__main__':
    compute=Compute()
