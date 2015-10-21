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

    def count(self, name):
        duermgr.counts(name)

    def get_url(self, name):
        return duermgr.get_url(name)

    def find_services(self, geo, category):
        return duermgr.FindServices(geo, category)

    def compute_content(self, content, user):
        if user not in users or 'geo' not in users[user]:
            return '需要您先发送一个位置信息，才能为您提供服务哦。\n点击输入框旁边的+，发送位置即可[微笑]','TEXT'
        category=duermgr.CheckServiceCategory(content, users[user].get('category',None))
        users[user]['category']=category
        if users[user]['category'] is not None:
            res, type=duermgr.Process(users[user], content)
            return res,type
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
            print lat, lng
            lng, lat=apitools.GeoConv(lng,lat)
            address, component=geocoder.GetAddress(lat, lng)
            user=xml.find('FromUserName').text
            users.setdefault(user, {})['address']=address.encode('utf-8')
            users.setdefault(user, {})['geo']=[lng,lat]
            users.setdefault(user, {})['city']=component['city'].encode('utf-8').rstrip('市')
            article={}
            article['title']='好的，现在小通可以为您提供服务了，以下内容应有尽有：\n\n'
            article['title']+='★充话费、电影票、演出票\n'
            article['title']+='★洗衣、保洁、保姆月嫂\n'
            article['title']+='★查快递、寄快递、同城搬家\n'
            article['title']+='★家电维修、手机数码维修回收、管道疏通、开锁换锁\n'
            article['title']+='★打车、找人代驾、汽车保养\n'
            article['title']+='★推拿、美容、美甲、美妆\n'
            article['title']+='★厨师上门、生鲜配送、外卖\n'
            article['title']+='★咖啡、水果、零食、香烟\n'
            return article['title'], 'TEXT'
        elif msgType=='image':
            image=xml.find('PicUrl').text
            return '图片信息：'+image, 'TEXT'
        elif msgType=='event':
            event=xml.find('Event').text
            if event=='subscribe':
                return '感谢您关注生活服务通，需要您先发送一个位置信息，才能为您提供服务哦：）\n点击输入框旁边的+，发送位置即可。', 'TEXT'
            elif event=='LOCATION':
                lat=xml.find('Latitude').text
                lng=xml.find('Longitude').text
                lng, lat=apitools.GeoConv(lng,lat)
                address, component=geocoder.GetAddress(lat, lng)
                user=xml.find('FromUserName').text
                users.setdefault(user, {})['address']=address.encode('utf-8')
                users.setdefault(user, {})['geo']=[lng, lat]
                users.setdefault(user, {})['city']=component['city'].encode('utf-8').rstrip('市')
            else:
                return '对不起，小通还不能理解您的问题[微笑]', 'TEXT'

if __name__=='__main__':
    compute=Compute()
