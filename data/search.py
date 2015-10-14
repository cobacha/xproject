#coding:utf-8
import sys
import string
import db_tools
from bson.son import SON

mydb=db_tools.connect()
items=mydb.service.find({})
for item in items:
    print item['rating'].encode('utf-8')
'''
r=mydb.command(SON([('geoNear', 'service'), ('near', [116.34, 39.99]), ('spherical', True), ('num', 1000), ('distanceMultiplier', 6378137), ('maxDistance', 5000.0/6378137), ('query', {'category': '搬家'})]))
for item in r['results']:
    obj=item['obj']
    print obj['telephone']
'''

