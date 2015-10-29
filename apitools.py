# -*- coding: utf-8 -*-
import sys
import string
import urllib
import urllib2
import json

apikey='69e6eeb71748a0f227ea9d524b079293'

def GetTuringRes(query, user):
    if user=='search_kuaidi':
        query='查快递"'+query+'"'
    elif user=='search_tianqi':
        query='查天气"'+query+'"'
    print query
    url = 'http://apis.baidu.com/turing/turing/turing?key=ca10fdaed1dae3e24ff2d277286e7dc8&info=%s&userid=%s' % (query, user)
    req = urllib2.Request(url)
    req.add_header('apikey', apikey)
    resp = urllib2.urlopen(req)
    content = resp.read()
    if content:
        obj=json.loads(content)
        return obj['text']

def GetWeather(city):
    url = 'http://apis.baidu.com/apistore/weatherservice/cityname?cityname='+city
    req = urllib2.Request(url)
    req.add_header('apikey', apikey)
    resp = urllib2.urlopen(req)
    content = resp.read()
    if content:
        obj=json.loads(content)['retData']
        return city+'当前天气：%s，%s℃，%s' % (obj['weather'].encode('utf-8'),obj['temp'].encode('utf-8'),obj['WS'].encode('utf-8'))
    return None

def GeoConv(lng,lat):
    url='http://api.map.baidu.com/geoconv/v1/?coords='+lng+','+lat+'&from=3&to=5&ak=cSkdmrGpRGBlts5uWq7wa4ef'
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)
    content = resp.read()
    if content:
        obj=json.loads(content)['result']
        return obj[0]['x'],obj[0]['y']
    return None

def GetMapServices(location, query):
    url='http://api.map.baidu.com/place/v2/search?query=%s&location=%f,%f&radius=8000&filter=sort_name:distance|sort_rule:1&output=json&scope=2&page_size=20&ak=cSkdmrGpRGBlts5uWq7wa4ef' %(query, location[1], location[0])
    req = urllib2.Request(url)
    resp = urllib2.urlopen(req)
    content = resp.read()
    if content:
        results=json.loads(content)['results']
        return results
    return None

if __name__=='__main__':
    print GetWeather('北京')
    print GetTuringRes('查快递"880350384879600241"', 'cxx')
    print GetMapServices([113.943257,22.524654], '医院')[0]['name'].encode('utf-8')
