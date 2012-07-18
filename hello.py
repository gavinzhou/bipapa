#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import urllib2
import tornado.escape
import json
import re

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug = True,
            )
        tornado.web.Application.__init__(self, handlers, **settings)

def search_api(keyword):
    host = "http://api.rakuten.co.jp/rws/3.0/json?"
    search_dict = {"developerId": "375ecf0e10025bd1489adffb9c51c018",
    		   "operation": "ItemSearch",
    		   "version": "2010-09-15"}
    search_dict["keyword"] = keyword
    search_list = []
    for key, value in search_dict.iteritems():
    	temp = '%s=%s' % (key, value)
    	search_list.append(temp)
    url = host + '&'.join(search_list)
    response = urllib2.urlopen(url)
    j = tornado.escape.json_decode(response.read())
    infos = j['Body']["ItemSearch"]["Items"]["Item"]
    url_list = []
    for info in infos:
        for key in info.keys():
            if key == "mediumImageUrl":
                url_list.append(info[key]) 
    return url_list
#            value = info[key]
#            if type(value) is unicode:
#                m = re.search(u'^http://(.*)(\.gif|\.jpg)', value)
#                if m:
#                    url_list.append(value) 
                
#    mgs = json.dumps(info, ensure_ascii=False)
#    return j['Body']["ItemSearch"]["Items"]["Item"][0]["mediumImageUrl"]
#    return mgs
#    json_html = response.read()
#    return json.dumps(json_html, sort_keys=True, indent=4)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template_test.html")
    
    def post(self):
        message=self.get_argument("message")
        mgs = search_api(message)
        self.render("template_mgs.html", message=mgs)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
