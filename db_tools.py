import sys
from pymongo import MongoClient

def connect():
    conn = MongoClient('localhost',27017)
    return conn.duer
