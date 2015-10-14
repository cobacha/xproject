#coding:utf-8
import sys
import string
import db_tools
import apitools
from bson.son import SON

mydb=db_tools.connect()

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
        service={'company':obj['company'], 'address':obj['address'], 'telephone':obj['telephone'], 'rating':obj['rating'], 'bookCount':obj['bookCount'], 'distance':FormatDistance(item['dis'])}
        services.append(service)
    return services

def ProcessKuaidi(info, content):
    res='对不起，我还不能理解你的问题：）'
    type='TEXT'
    if '查快递' in content:
        res=apitools.GetTuringRes(content, 'search_kuaidi')
        info['status']='search'
    elif 'status' in info and info['status']=='search':
        res=apitools.GetTuringRes(content, 'search_kuaidi')
    elif '寄快递' in content:
        res='请问您对快递公司有要求吗，如无特殊要求，小度将为您自筛选：）'
    elif '顺丰' in content:
        res=[]
        article={}
        article['title']='顺丰速运寄件信息'
        article['pic']='http://188.166.241.25/static/imgs/logo/shunfeng.png'
        res.append(article)
        article={}
        article['title']='客服专线: 95338'
        res.append(article)
        article={}
        article['title']='点此进入网上预约寄件'
        article['url']='http://www.sf-express.com/mobile/cn/sc/dynamic_functions/ship/ship.html'
        res.append(article)
        article={}
        article['title']='附近的服务网点信息\n\n地址：blabla\n电话：1380000000\n评分：4.5\n距离：1.1公里'
        res.append(article)
        type='NEWS'
    elif '圆通' in content:
        res=[]
        article={}
        article['title']='圆通快递寄件信息'
        article['pic']='http://188.166.241.25/static/imgs/logo/yuantong.jpg'
        res.append(article)
        article={}
        article['title']='客服专线: 95554'
        res.append(article)
        article={}
        article['title']='点此进入网上预约寄件'
        article['url']='http://wap.yto.net.cn/OrderManage/OnlineOrders.htm'
        res.append(article)
        article={}
        article['title']='附近的服务网点信息\n\n地址：blabla\n电话：13800000000\n评分：4.5\n距离：1.1公里'
        res.append(article)
        type='NEWS'
    elif '没有' in content or '无' in content:
        res=[]
        article={}
        article['title']='小度为您找到以下快递信息:'
        res.append(article)
        article={}
        article['title']='快递100\n提供上百家常用快递、物流公司的快递单号查询、快递网点电话查询、快递价格查询、网上寄快递服务。'
        article['pic']='http://188.166.241.25/static/imgs/logo/kuaidi100.png'
        article['url']='http://m.kuaidi100.com/courier/search.jsp'
        res.append(article)
        article={}
        article['title']='附近的服务网点信息\n\n名称：blabla\n地址：blabla\n电话：13800000000\n评分：4.5\n距离：1.1公里'
        res.append(article)
        type='NEWS'
    return res, type

def ProcessBaojie(info, content):
    res='对不起，我还不能理解您的问题：）'
    type='TEXT'
    return res,type

def Process(info, content):
    if info['category']=='快递':
        return ProcessKuaidi(info, content)
    elif info['category']=='家庭保洁':
        return ProcessBaojie(info, content)
    else:
        return 'OK', 'TEXT'

categorys={}
f=open('data/cat.map')
for line in f:
    s=line.strip().split('\t')
    categorys[s[0]]=s[1]

def CheckServiceCategory(query):
    for category in categorys:
        if category in query:
            return categorys[category]
    return None

if __name__=='__main__':
    services=FindServices([113.936447, 22.546457], '搬家')
    for s in services:
        print s['company'], s['address'], s['distance'], s['rating'], s['bookCount'], s['telephone']
