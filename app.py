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
            (r"/genreid/(\d+)?", GenreIdHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug = True,
            )
        tornado.web.Application.__init__(self, handlers, **settings)

def rakuten_api(**parts):
    host = "http://api.rakuten.co.jp/rws/3.0/json?"
    search_dict = {"developerId" : "375ecf0e10025bd1489adffb9c51c018"}
    search_dict.update(parts)
    search_list = []
    for key, value in search_dict.iteritems():
    	temp = '%s=%s' % (key, value)
    	search_list.append(temp)
    url = host + '&'.join(search_list)
    response = urllib2.urlopen(url)
    api_result = tornado.escape.json_decode(response.read())
    return api_result

class GenreIdHandler(tornado.web.RequestHandler):
    """docstring for GenreIdHandler"""
    def get(self, genreId):
        if genreId is None:
            genreId = 0
        mgs = rakuten_api(operation="GenreSearch", 
                          version = "2007-04-11", 
                          genreId = genreId)
        mgs_list = mgs["Body"]["GenreSearch"]["child"]
        self.render("genreid.html", message=mgs_list)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
    
    def post(self):
        keyword=self.get_argument("message")
        mgs = rakuten_api(operation="ItemSearch", 
                          version="2010-09-15", 
                          keyword=keyword)
        mgs_list = mgs['Body']["ItemSearch"]["Items"]["Item"]
        self.render("template_mgs.html", message=mgs_list)

def main():
    tornado.options.options['log_file_prefix'].set('./logs/app.log')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
