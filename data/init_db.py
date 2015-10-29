#coding:utf-8
import sys
import string
import db_tools
import json
import random
from pymongo import ASCENDING


mydb=db_tools.connect()
mydb.service.remove()


def GetPhone():
    return random.choice(['186', '133', '139','188','185','136','158','151'])+"".join(random.choice("0123456789") for i in range(8))

def GetRating():
    return str(round(random.random()*2+3,1))

def GetCount():
    return str(random.randint(1, 1000))

f=open('58.all.final')
had={}
for line in f:
    s=json.loads(line.strip())
    if s['datePosted']<'2015':
        continue
    if s['company']+','+str(s['location']) in had:
        continue
    had[s['company']+','+str(s['location'])]=1

    if 'rating' not in s or s['rating']=='':
        s['rating']='0.0'
    s['location']={'type': 'Point', 'coordinates': s['location']}
    mydb.service.save(s)
mydb.service.ensure_index([('location','2dsphere'), ('category', ASCENDING)])
