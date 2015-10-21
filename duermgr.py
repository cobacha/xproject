#coding:utf-8
import sys
import string
import db_tools
import apitools
import geocoder
import urllib2
import random
from bson.son import SON

mydb=db_tools.connect()
service_counts={}

h5_src={}
urls={}
f=open('data/h5_src.txt')
for line in f:
    s=line.strip().split('\t')
    h5={}
    h5['name']=s[1]
    h5['desc']=s[2]
    h5['pic']=s[3]
    h5['url']='http://188.166.241.25/redirect?name='+h5['name']
    urls[s[1]]=s[4]
    service_counts[s[1]]=random.randint(1,20)
    h5_src.setdefault(s[0],[]).append(h5)

def get_url(name):
    return urls.get(name,'m.baidu.com')

def counts(name):
    service_counts[name]=service_counts.get(name,0)+1

def FormatDistance(distance):
    if int(distance/1000)==0:
        return str(int(distance))+'米'
    elif int(distance/1000)<10:
        return str(round(distance/1000,1))+'千米'
    else:
        return str(int(distance/1000))+'千米'

def FindServices(location, category):
    r=mydb.command(SON([('geoNear', 'service'), ('near', location), ('spherical', True), ('num', 10), ('distanceMultiplier', 6378137), ('maxDistance', 20000.0/6378137), ('query', {'category': category})]))
    services=[]
    for item in r['results']:
        obj=item['obj']
        service={'company':obj['company'].encode('utf-8'), \
                 'address':obj['address'].encode('utf-8'), \
                 'telephone':obj['telephone'].encode('utf-8'), \
                 'rating':obj['rating'].encode('utf-8'), \
                 'bookCount':obj['bookCount'].encode('utf-8'), \
                 'fromUrl':obj['fromUrl'].encode('utf-8'), \
                 'distance':FormatDistance(item['dis'])}
        services.append(service)
    if len(services)<=3:
        results=apitools.GetMapServices(location,category)
        for item in results:
            service={'company':item['name'].encode('utf-8'), \
                     'address':item['address'].encode('utf-8'), \
                     'telephone':item.get('telephone','').encode('utf-8'), \
                     'distance':FormatDistance(geocoder.GetDistance(item['location']['lng'], item['location']['lat'], location[0], location[1]))}
            services.append(service)
    return services

def ProcessKuaidi(info, content):
    res='请问您是要寄快递还是查快递呢？'
    type='TEXT'
    if '查快递' in content:
        res=apitools.GetTuringRes(content, 'search_kuaidi')
        info['status']='search'
    elif 'status' in info and info['status']=='search':
        res=apitools.GetTuringRes(content, 'search_kuaidi')
    elif '寄快递' in content:
        res='请问您有指定的快递公司吗？'
    elif '顺丰' in content:
        res=[]
        article={}
        article['title']='顺丰速运服务信息'
        article['pic']='http://188.166.241.25/static/imgs/logo/shunfeng.png'
        res.append(article)
        article={}
        article['title']='客服专线: 95338'
        article['url']='tel://95338'
        res.append(article)
        article={}
        article['title']='点此进入网上预约寄件'
        article['url']='http://www.sf-express.com/mobile/cn/sc/dynamic_functions/ship/ship.html'
        res.append(article)
        type='NEWS'
    elif '圆通' in content:
        res=[]
        article={}
        article['title']='圆通快递服务信息'
        article['pic']='http://188.166.241.25/static/imgs/logo/yuantong.jpg'
        res.append(article)
        article={}
        article['title']='客服专线: 95554'
        article['url']='tel://95554'
        res.append(article)
        article={}
        article['title']='点此进入网上预约寄件'
        article['url']='http://wap.yto.net.cn/OrderManage/OnlineOrders.htm'
        res.append(article)
        type='NEWS'
    elif '没有' in content or '无' in content:
        return ProcessNormal(info, content)
    return res, type

def ProcessNormal(info, content):
    res=[]
    article={}
    article['title']='小通为您找到以下'+info['category']+'服务信息：'
    res.append(article)
    if info['category'] in h5_src:
        for index, article in enumerate(h5_src[info['category']]):
            if index==0:
                article['title']=article['name']+'\n●'+str(service_counts.get(article['name'],0))+'人使用过'
            else:
                article['title']=article['name']
            res.append(article)
    services=FindServices(info['geo'],info['category'])
    if len(services)>0:
        article={}
        article['title']='附近认证的服务网点'
        article['url']='http://188.166.241.25/service?category='+info['category']+'&geo='+str(info['geo'][0])+','+str(info['geo'][1])
        res.append(article)
        for service in services[:3]:
            article={}
            article['title']=service['company']+'（'+service['distance']+'）'
            res.append(article)
        res.append(article)

    if len(res)>1:
        return res,'NEWS'
    else:
        return '对不起，暂时还不能给您提供相关的服务信息，小通正在努力地建设中，敬请期待[微笑]', 'TEXT'


def Process(info, content):
    if info['category']=='天气':
        return apitools.GetWeather(info['city']),'TEXT'
    elif info['category']=='快递':
        return ProcessKuaidi(info, content)
    else:
        return ProcessNormal(info, content)

categorys={}
f=open('data/cat.map')
for line in f:
    s=line.strip().split('\t')
    categorys[s[0]]=(s[1],s[2])

def CheckServiceCategory(query, last):
    for category in categorys:
        item=categorys[category]
        if category in query and (item[1]=='0' or item[0]==last):
            return item[0]
    return None

if __name__=='__main__':
    services=FindServices([113.936447, 22.546457], '医院')
    for s in services:
        print s['company'], s['address'], s['distance']
