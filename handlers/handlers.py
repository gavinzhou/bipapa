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
import urllib2
import tornado.escape
import pymongo,gridfs
import bcrypt

import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from module.rakuten_api import rakuten_api

from tornado.options import define, options

class BaseHandler(tornado.web.RequestHandler):
    def get_login_url(self):
        return u"/login"

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
        else:
            return None
    
    @property        
    def db(self):
        """mongodb settings"""
        if not hasattr(BaseHandler, "_db"):
            _db = pymongo.Connection().bipapa
        return _db
        
    @property
    def fs(self):
        if not hasattr(BaseHandler,"_fs"):
            db = pymongo.Connection().gridfs
            _fs = gridfs.GridFS(db)
        return _fs
        
class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        email = self.get_argument("email", "")
        password = self.get_argument("password", "")

        user = self.db['users'].find_one({'user':email})

        if user and user['password'] and bcrypt.hashpw(password, user['password']) == user['password']:
            self.set_current_user(email)
            self.redirect("hello")
        else:
            error_msg = u"?notification=" + tornado.escape.url_escape("Login incorrect.")
            self.redirect(u"register" + error_msg)

    def set_current_user(self, user):
        print "setting" + user
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

class RegisterHandler(LoginHandler):
    def get(self):
        '''
        logging exp
        logging.info("**Request to RegisterHandler!")
        '''
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
    
            userId = self.application.db['users'].save(user)
            logging.info("user ObjectId is %s" % userId)
            self.set_current_user(email)
    
            self.redirect("hello")

class TwitterLoginHandler(LoginHandler, tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            logging.info("twitter oauth_token is %s" % self.get_argument("oauth_token", None))
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authorize_redirect("/twitter_login")

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Twitter auth failed")
        logging.info("twitter Auth worked")

        userId = self.db['users'].save(user)
        self.set_current_user(user['username'])
        self.redirect("hello")

class FacebookLoginHandler(LoginHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument('code', False):
            self.get_authenticated_user(
                redirect_uri=self.settings['facebook_registration_redirect_url'],
                client_id=self.application.settings['facebook_app_id'],
                client_secret=self.application.settings['facebook_secret'],
                code=self.get_argument('code'),
                callback=self.async_callback(self._on_login)
            )
            return

        self.authorize_redirect(redirect_uri=self.settings['facebook_registration_redirect_url'],
                                client_id=self.settings['facebook_app_id'])

    def _on_login(self, user):
        if not user:
            self.clear_allcookies()
            raise tornado.web.HTTPError(500, 'Facebook authentication failed')
        logging.info("facebook Auth worked")
        logging.info(user['access_token'])
        self.facebook_request("/me", access_token=user['access_token'], callback=self._save_user_profile)
        self.set_current_user(user['name'])
        self.redirect('hello')

    def _save_user_profile(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook authentication failed.")
        userId = self.db['users'].save(user)

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/login")

class HelloHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        logging.info("user is %s" % user)
        self.render("hello.html", user=user)

    def post(self):
        return self.get()

class ViewImageHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self,filename):
        name,sep,ext = filename.rpartition(".")
        if not sep:
            img_name = ext
        else:
            img_name = name
        img_file = self.fs.get_version(filename=img_name)
        self.add_header('Content-Type',img_file.content_type)
        self.write(img_file.read())
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

class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        filename_list = self.fs.list()
        self.render("index.html", filename_list=filename_list)

    def post(self):
        keyword = self.get_argument("message")
        keyword = urllib2.quote(keyword.encode('utf-8'))
        mgs = rakuten_api(operation="ItemSearch", 
                          version="2010-09-15", 
                          keyword=keyword)
        mgs_list = mgs['Body']["ItemSearch"]["Items"]["Item"]
        self.render("template_mgs.html", message=mgs_list)
