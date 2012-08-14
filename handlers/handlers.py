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
import tornado.web
import urllib2
import tornado.escape
import json
import pymongo
import bcrypt
from module.rakuten_api import rakuten_api

from tornado.options import define, options
from pymongo import Connection
from gridfs import GridFS

db = Connection().gridfs
fs = GridFS(db)


def getimg4db(filename):
    f = fs.get_version(filename="%s" %filename)
    img = f.read()
    content_type = f.content_type
    db.close
    return content_type,img
        
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")

    def post(seflf):
        email = self.get_argument("email", "")
        password = self.get_argument("password", "")

        user = self.application.db['users'].find_one({'user':email})

        if user and user['password'] and bcrypt.hashpw(password, user['password']) == user['password']:
            self.set_current_user(email)
            self.redirect("/")
        else:
            error_msg = u"?notification=" + tornado.escape.url_escap("Login incorrect.")
            self.redirect(u"/login" + error_msg)

    def set_current_user(self, user):
        print "setting" + user
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

class RegisterHandler(LoginHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        email = self.get_argument("email", "")

        already_taken = self.application.db["users"].find_one({'user': email})
        if already_taken:
            error_msg = u"?error=" + tornado.escape.url_escape("Login name already taken")
            self.write(error_msg)
            self.redirect(u"/login" + error_msg)
        else:
            password = self.get_argument("password", "")
            hashed_pass = bcrypt.hashpw(password, bcrypt.gensalt(8))
    
            user = {}
            user['user'] = email
            user['password'] = hashed_pass
    
            auth = self.application.db['users'].save(user)
            self.set_current_user(email)
    
            self.redirect("/")

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect(u"/")

class ViewImageHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self,filename):
        name,sep,ext = filename.rpartition(".")
        if not sep:
            content_type, img = getimg4db(ext)
        else:
            content_type, img = getimg4db(name)
        self.set_header('Content-Type',content_type)
        self.write(img)
        self.finish()
        
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

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        filename_list = fs.list()
        self.render("index.html", filename_list=filename_list)

    def post(self):
        keyword = self.get_argument("message")
        keyword = urllib2.quote(keyword.encode('utf-8'))
        mgs = rakuten_api(operation="ItemSearch", 
                          version="2010-09-15", 
                          keyword=keyword)
        mgs_list = mgs['Body']["ItemSearch"]["Items"]["Item"]
        self.render("template_mgs.html", message=mgs_list)
