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
    h5['pic']='http://188.166.241.25/static/imgs/logo/'+s[3]
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

def FindServices(location, query):
    r=mydb.command(SON([('geoNear', 'service'), ('near', location), ('spherical', True), ('num', 10), ('distanceMultiplier', 6378137), ('maxDistance', 20000.0/6378137), ('query', {'category': query})]))
    services=[]
    had={}
    for item in r['results']:
        obj=item['obj']
        service={'company':obj['company'].encode('utf-8'), \
                 'address':obj['address'].encode('utf-8'), \
                 'telephone':obj['telephone'].encode('utf-8'), \
                 'rating':obj['rating'].encode('utf-8'), \
                 #'bookCount':obj['bookCount'].encode('utf-8'), \
                 'fromUrl':obj['fromUrl'].encode('utf-8'), \
                 'distance':FormatDistance(item['dis'])}
        if service['telephone'] not in had:
            had[service['telephone']]=1
            services.append(service)
    if len(services)<=3:
        results=apitools.GetMapServices(location,query)
        for item in results:
            if 'telephone' not in item or '%' in item['telephone'] or ',' in item['telephone'] or 'detail_url' not in item['detail_info']:
                continue
            service={'company':item['name'].encode('utf-8'), \
                     'address':item['address'].encode('utf-8'), \
                     'rating':item['detail_info'].get('overall_rating','0'), \
                     'telephone':item['telephone'].encode('utf-8'), \
                     'fromUrl':item['detail_info']['detail_url'], \
                     'distance':FormatDistance(float(item['detail_info']['distance']))}
            if service['telephone'] not in had:
                had[service['telephone']]=1
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
        info['status']=None
        info['category']=None
    elif '寄快递' in content:
        res='请问您有指定的快递公司吗？'
    elif '没有' in content or '无' in content:
        return ProcessNormal(info, content)
    return res, type

def ProcessNormal(info, content):
    res=[]
    article={}
    res.append(article)

    if info['category'] in h5_src:
        article={}
        article['title']='☞认证的'+info['category']+'服务平台：'
        res.append(article)
        for index, article in enumerate(h5_src[info['category']]):
            if index==0:
                article['title']=article['name']+'（'+str(service_counts.get(article['name'],0))+'人使用过）'
            else:
                article['title']=article['name']
            article['url']=article['url']
            res.append(article)
    services=FindServices(info['geo'],info['query'])
    if len(services)>0:
        article={}
        article['title']='☞附近认证的服务网点：'
        article['url']='http://188.166.241.25/service?category='+info['query']+'&geo='+str(info['geo'][0])+','+str(info['geo'][1])
        res.append(article)
        for service in services[:3]:
            article={}
            article['title']=service['company']+'（'+service['distance']+'）'
            article['url']=service['fromUrl']
            res.append(article)

    if len(res)>1:
        article={}
        article['title']='亲，以上信息对您有帮助吗？有请回复1，没有请回复2，谢谢：）'
        res.append(article)
        info['status']='feedback'
        return res,'NEWS'
    else:
        return '对不起，暂时还不能给您提供相关的服务信息，小通正在努力地建设中，敬请期待[微笑]', 'TEXT'


def Process(info, content):
    if info['category']=='天气':
        return apitools.GetTuringRes(info['city'],'search_tianqi'),'TEXT'
    elif info['category']=='快递':
        return ProcessKuaidi(info, content)
    else:
        return ProcessNormal(info, content)

categorys={}
f=open('data/cat.map')
for line in f:
    s=line.strip().split('\t')
    categorys[s[0]]=(s[1],s[2],s[3])

def CheckServiceCategory(query, last):
    for category in categorys:
        item=categorys[category]
        if category in query and (item[2]=='0' or item[0]==last):
            return item[0],item[1]
    return None,None

if __name__=='__main__':
    services=FindServices([113.936447, 22.546457], '医院')
    for s in services:
        print s['company'], s['address'], s['distance']
