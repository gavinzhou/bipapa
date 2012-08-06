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

import logging

import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado import template
import tornado.web
import urllib2
import tornado.escape
import json
import re
import pymongo
import pycurl
import StringIO

from multiprocessing import Pool
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/genreid/(\d+)?", GenreIdHandler),
            (r"/searchgenreid/(\d+)?", SearchGenreIdHandler),
            (r"/ranking", RankingHandler)
        ]
        conn = pymongo.Connection("localhost", 27017)
        self.db = conn["bipapa"]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            pool = Pool(2),
            debug = True,
            )
        tornado.web.Application.__init__(self, handlers, **settings)

#def rakuten_api(**parts):
#    host = "http://api.rakuten.co.jp/rws/3.0/json?"
#    search_dict = {"developerId" : "375ecf0e10025bd1489adffb9c51c018"}
#    search_dict.update(parts)
#    search_list = []
#    for key, value in search_dict.iteritems():
#    	temp = '%s=%s' % (key, value)
#    	search_list.append(temp)
#    url = host + '&'.join(search_list)
#    response = urllib2.urlopen(url)
#    c = pycurl.Curl()
#    c.setopt(pycurl.URL, url)
#    b = StringIO.StringIO()
#    c.setopt(pycurl.WRITEFUNCTION, b.write)
#    c.setopt(pycurl.FOLLOWLOCATION, 1)
#    c.setopt(pycurl.MAXREDIRS, 5)
#    c. perform()
#    response = b.getvalue()
#    api_result = tornado.escape.json_decode(response)
#    api_result = tornado.escape.json_decode(response.read())
#    return api_result

class RankingHandler(tornado.web.RequestHandler):
    def get(self):
        mgs = rakuten_api(operation="ItemRanking",
                          version = "2010-08-05",
                          sex = "1",
                          age = "20")
        mgs_list = mgs['Body']['ItemRanking']['Items']['Item']
        self.render("ranking.html", message=mgs_list)

class SearchGenreIdHandler(tornado.web.RequestHandler):
    """docstring for GenreIdHandler"""
    def get(self, genreId):
        coll = self.application.db.genreId
        genreId_doc = []
        if genreId is None:
            genreId_list = coll.find({"genreLevel" : 1}, {"_id":0})
        else:
            genreId_list = coll.find({"genreId" : int(genreId)}, {"_id":0})
        if genreId_list:
            for data in genreId_list:
                genreId_doc.append(data)
            self.render("searchgenreid.html", message=genreId_doc)
        else:
            self.set_status(404)
            self.write("error genreId not found")

    def post(self, genreId):
        genreId = self.get_argument("genreId")     
        coll = self.application.db.genreId
        genreId_doc = []
        if genreId is None:
            genreId_list = coll.find({"genreLevel" : 1}, {"_id":0})
        else:
            genreId_list = coll.find({"genreId" : int(genreId)}, {"_id":0})
        if genreId_list:
            for data in genreId_list:
                genreId_doc.append(data)
            self.render("searchgenreid.html", message=genreId_doc)
        else:
            self.set_status(404)
            self.write("error genreId not found")
        
class GenreIdHandler(tornado.web.RequestHandler):
    def get(self, genreId):
        if genreId is None:
            genreId = 0
        mgs = rakuten_api(operation="GenreSearch", 
                          version = "2007-04-11", 
                          genreId = genreId)
        if mgs["Header"]["Status"] == "Success":
            grenreid_doc  = mgs["Body"]["GenreSearch"]
            self.render("genreid.html", message = grenreid_doc)
        else:
            logging.error(mgs["StatusMsg"])
            self.set_status(404)
            self.write("error genreId not found")

def getimg4db(filename):
    from pymongo import Connection
    from gridfs import GridFS
    db = Connection().gridfs
    fs = GridFS(db)
    f = fs.get_version(filename="%s" %filename)
    img = f.read()
    content_type = f.content_type
#    id_list = fs.list()
#    img_list = []
#    dic_list = []
#    for id in id_list:
#        img_list.append(fs.get_version(id).read())
#        dic_list.append(fs.get_version(id).content_type)
#    return (img_list, dic_list)
    db.close
    return img,content_type
        
class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        from pymongo import Connection
        from gridfs import GridFS
        db = Connection().gridfs
        fs = GridFS(db)
        id_list = fs.list()
        for id in id_list:
            img,content_type = getimg4db("501b745a41ab10241f6d0393")
            self.set_header("Content-Type", content_type)
            self.write(img)
            self.finish()
#        self.set_header("Content-Length", len(img_list[8]))
#        self.write(img_list[8])
#        self.write(img_list[9])
#        self.render("index.html", img_list=img_list[9])
#        self.finish('<html><form enctype="multipart/form-data" action="/upload" method="post">Upload File: <input type="file" name="file1" /><input type="submit" value="upload" />')
    
    def post(self):
        keyword = self.get_argument("message")
        keyword = urllib2.quote(keyword.encode('utf-8'))
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
