# coding: UTF-8
import os
import web

from weixinInterface import WeixinInterface
from weixinTest import WeixinTest

urls = (
       '/weixin','WeixinInterface',
       '/weixintest', 'WeixinTest'
)

render = web.template.render('template')
web.config.debug = False
PWD = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(PWD, "static")
web.config.static_path = static_path

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
