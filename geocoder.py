#coding:utf-8
import sys
import string
import requests
import json
import math

def GetGeo(location):
    url='http://apis.map.qq.com/ws/geocoder/v1/?address='+location+'&key=YMUBZ-UDIKI-FOZGR-57E7J-7GHQE-4WBOB'
    r=requests.get(url)
    lat=r.json()['result']['location']['lat']
    lng=r.json()['result']['location']['lng']
    return lng, lat

def GetAddress(lat, lng):
    url='http://apis.map.qq.com/ws/geocoder/v1/?location='+str(lat)+','+str(lng)+'&key=YMUBZ-UDIKI-FOZGR-57E7J-7GHQE-4WBOB&get_poi=1'
    r=requests.get(url)
    res=r.json()['result']
    return res['formatted_addresses']['recommend'], res['address_component']

EARTH_RADIUS = 6378.137 #地球半径
def rad(d):
    return d * math.pi / 180.0;

def GetDistance(lng1, lat1, lng2, lat2):
    radLat1 = rad(lat1)
    radLat2 = rad(lat2)
    a = radLat1 - radLat2
    b = rad(lng1) - rad(lng2)

    s = 2 * math.sin(math.sqrt(math.pow(math.sin(a/2),2) + math.cos(radLat1)*math.cos(radLat2)*math.pow(math.sin(b/2),2)))
    s = s * EARTH_RADIUS
    s = round(s * 10000) / 10000
    return s

def GetCostTime(lng1, lat1, lng2, lat2):
    s=GetDistance(lng1, lat1, lng2, lat2)
    return s/20*60

if __name__=='__main__':
    lng1, lat1=GetGeo('北京五道口地铁站')
    lng2, lat2=GetGeo('北京中关村')
    print GetDistance(lng1, lat1, lng2, lat2)
    print GetCostTime(lng1, lat1, lng2, lat2)
