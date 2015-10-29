import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import string
import json

cats={}
f=open('category.uniq')
for line in f:
    s=line.strip().split('\t')
    cats[s[0]]=s[1]

f=open('58.bj.cxx')
for line in f:
    s=json.loads(line.strip())
    s['category']=cats[s['category'].encode('utf-8')]
    print json.dumps(s, ensure_ascii=False)
