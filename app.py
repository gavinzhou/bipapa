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
import tornado.escape
import pymongo
import base64, uuid

from module.rakuten_api import rakuten_api
from handlers.handlers import *

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            # main handler
            (r"/", MainHandler),
            (r"/genreid/(\d+)?", GenreIdHandler),
            (r"/searchgenreid/(\d+)?", SearchGenreIdHandler),

            # image server
            (r"/view/(.*)", ViewImageHandler),

            (r"/ranking", RankingHandler),

            # auth
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/register", RegisterHandler),

            (r"/twitter_login", TwitterLoginHandler),
            (r"/facebook_login", FacebookLoginHandler),

            (r"/hello", HelloHandler),
        ]
        conn = pymongo.Connection("localhost", 27017)
        self.db = conn["bipapa"]
        settings = {
            "template_path" : os.path.join(os.path.dirname(__file__), "templates"),
            "static_path" : os.path.join(os.path.dirname(__file__), "static"),
            "cookie_secret" : base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "twitter_consumer_key": "IR6TQE5y8Q0LMIeEPIs5w",
            "twitter_consumer_secret": "3lUtS7oCeJoJx6VuoCAdKxMovJnYy3NHcR8GdgOBOXU",
            'facebook_app_id': '106387102723201',
            'facebook_secret': '8f468511877dab8fbacc0743a7050405',
            'facebook_registration_redirect_url': 'http://10.24.94.36:8888/facebook_login',
            "xsrf_cookies" : True,
            "debug" : True,
            }

        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.options['log_file_prefix'].set('logs/app.log')
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
