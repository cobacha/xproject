# -*- coding: utf-8 -*-
import sys
import string
import geocoder
import urllib2
import apitools
import duermgr
import logging

logging.basicConfig(level=logging.DEBUG, \
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', \
                    datefmt='%a, %d %b %Y %H:%M:%S', \
                    filename='duer.log', \
                    filemode='a+')
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
        if 'feedback'==users[user].get('status',None):
            users[user]['status']=None
            if '1'==content:
                logging.info('user='+user+'; category='+str(users[user].get('category','None'))+'; feedback=1')
                return '谢谢亲，很高兴小通提供的信息对您有帮助，请问还有什么可以帮到亲的吗：）','TEXT'
            elif '2'==content:
                logging.info('user='+user+'; category='+str(users[user].get('category','None'))+'; feedback=2')
                return '很抱歉，没有帮到亲T_T 小通会继续努力的＼(*⌒0⌒)♪','TEXT'
        category,query=duermgr.CheckServiceCategory(content, users[user].get('category',None))
        if users[user].get('status',None) is None:
            users[user]['category']=category
            users[user]['query']=query
        if users[user]['category'] is not None or users[user].get('status',None) is not None:
            logging.info('user='+user+'; category='+str(users[user].get('category','None'))+'; status='+str(users[user].get('status','None')))
            res, type=duermgr.Process(users[user], content)
            return res,type
        else:
            return '很抱歉，我还不能理解你的问题，不如对我说：我要修手机[微笑]','TEXT'

    def compute(self, xml):
        user=xml.find('FromUserName').text
        msgType=xml.find('MsgType').text

        if msgType=='text':
            content=xml.find('Content').text.encode('utf-8')
            logging.info('user='+user+'; text='+content)
            return self.compute_content(content, user)
        elif msgType=='voice':
            content=xml.find('Recognition').text.encode('utf-8')
            logging.info('user='+user+'; voice='+content)
            return self.compute_content(content, user)
        elif msgType=='location':
            lat=xml.find('Location_X').text
            lng=xml.find('Location_Y').text
            lng, lat=apitools.GeoConv(lng,lat)
            logging.info('user='+user+'; geo='+str(lng)+','+str(lat))
            address, component=geocoder.GetAddress(lat, lng)
            logging.info('user='+user+'; address='+address)
            users.setdefault(user, {})['address']=address.encode('utf-8')
            users.setdefault(user, {})['geo']=[lng,lat]
            users.setdefault(user, {})['city']=component['city'].encode('utf-8').rstrip('市')
            article={}
            article['title']='好的，现在小通可以为您提供服务了，以下内容应有尽有：\n\n'
            article['title']+='★洗衣洗鞋、家庭保洁、保姆月嫂\n'
            article['title']+='★查寄快递、搬家\n'
            article['title']+='★推拿、美容、美甲、美妆\n'
            article['title']+='★厨师上门、生鲜配送、外卖\n'
            article['title']+='★水果、蔬菜、汽车保养\n'
            article['title']+='★家电维修、家电清洗、数码维修回收\n'
            article['title']+='★家具维修、房屋防水、管道疏通、开锁换锁\n'
            return article['title'], 'TEXT'
        elif msgType=='image':
            image=xml.find('PicUrl').text
            return '图片信息：'+image, 'TEXT'
        elif msgType=='event':
            event=xml.find('Event').text
            if event=='subscribe':
                return '恭喜你，终于Get到了生活服务通！需要您先发送一个位置信息，才能为您提供服务哦：）\n点击输入框旁边的+，发送位置即可。', 'TEXT'
            elif event=='LOCATION':
                lat=xml.find('Latitude').text
                lng=xml.find('Longitude').text
                lng, lat=apitools.GeoConv(lng,lat)
                logging.info('user='+user+'; geo:'+str(lng)+','+str(lat))
                address, component=geocoder.GetAddress(lat, lng)
                logging.info('user='+user+'; address='+address)
                users.setdefault(user, {})['address']=address.encode('utf-8')
                users.setdefault(user, {})['geo']=[lng, lat]
                users.setdefault(user, {})['city']=component['city'].encode('utf-8').rstrip('市')
            else:
                return '对不起，小通还不能理解您的问题[微笑]', 'TEXT'

if __name__=='__main__':
    compute=Compute()
