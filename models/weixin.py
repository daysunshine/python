#!/usr/bin/python3

import urllib.request
import urllib
import json
import logging
import requests
import os

class WeiXin:

    def __init__(self):
        self.corpid = 'xxxxx'
        self.corpsecret = 'xxxxxx'

    def weixin(self, title, content):
        try:
            baseurl = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}".format(self.corpid,self.corpsecret)
            request = urllib.request.Request(baseurl)
            response = urllib.request.urlopen(request)
            ret = response.read().decode('utf-8', 'ignore')
            dd = eval(ret)
            mytoken = dd["access_token"]
            url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={0}".format(mytoken)
            payload = {
                "touser": "@all",
                "msgtype": "text",
                "agentid": "1000002",
                "text": {
                    "content": "主题:{0}\n内容:{1}".format(title, content)
                },
                "safe": "0"
            }
            headers = {'Content-Type': 'application/json'}
            to_post = requests.post(url, headers=headers, data=json.dumps(payload))
        except Exception as e:
            print(e)

    def send(self, tt, cc):
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option("-t", "--title", dest="title", default=tt, )
        parser.add_option("-c", "--content", dest="content", default=cc, )
        (options, args) = parser.parse_args()
        self.weixin(options.title, options.content)
