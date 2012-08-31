#!/usr/bin/env python
# coding: utf-8

import tornado.escape
import pycurl, urllib
import StringIO
#import simplejson as json
import time
import pymongo

from getimg2db import GetImg2db

class RakutenAPI(object):
    def result(self, params):
        """__init__ start"""
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c.setopt(pycurl.MAXREDIRS, 5)
        self.c.setopt(pycurl.URL, 'http://api.rakuten.co.jp/rws/3.0/json?')
        self.c.setopt(pycurl.TIMEOUT, 30)
        self.c.setopt(pycurl.POST, 1)
        """__init__ end"""

        b = StringIO.StringIO()
        params["developerId"] = "375ecf0e10025bd1489adffb9c51c018"
        params = urllib.urlencode(params)
        self.c.setopt(pycurl.POSTFIELDS, params)
        self.c.setopt(pycurl.WRITEFUNCTION, b.write)
        self.c.perform()
        self.c.close()
        response = b.getvalue()
        _result = tornado.escape.json_decode(response)
        time.sleep(1)
        return _result

class GetAPI(RakutenAPI):
    def ItemRanking(self, genreid, page=1):
        params = dict(operation="ItemRanking",
                          version = "2010-08-05",
                          page = page,
                          genreId = genreid)
        msg = self.result(params)
        if msg['Header']['Status'] == 'Success':
            return msg['Body']['ItemRanking']
        else:
            return msg['Header']['StatusMsg']

    def ItemSearch(self, keyword, page):
        params = dict(operation="ItemSearch",
                          version = "2010-09-15",
                          page = page,
                          keyword = keyword,)
        msg = self.result(params)
        if msg['Header']['Status'] == 'Success':
            return msg['Body']['ItemSearch']
        else:
            return msg['Header']['StatusMsg']

def db():
    """mongodb settings"""
    if not hasattr(BaseHandler, "_db"):
        _db = pymongo.Connection().bipapa
    return _db

def getItem(keyword, coll_name, page=1):
    """ get item from rakuten api """
    coll = db[coll_name]
    getapi = GetAPI()
    itemresult = getapi.ItemSearch(keyword, page)
    if page < itemresult["pageCount"]:
        for item in itemresult["Items"]["Item"]:
            _item = {}
            _item["itemName"]       =   item["itemName"]
            _item["itemImageUrl"]   =   item["mediumImageUrl"].split("?")[0]           
            _item["itemPrice"]      =   item["itemPrice"]
            _item["genreId"]        =   item["genreId"]
            _item["itemUrl"]        =   item["itemUrl"]
            
            if not coll.find_one(_item):
                coll.insert(_item)
        getItem(keyword, coll_name, page + 1)

def getCollId(keyword):    
    COLLECTION_NAME = "KeywordList"
    try:
        coll = db.create_collection(COLLECTION_NAME)
    except CollectionInvalid:
        coll = db[COLLECTION_NAME]
    rz = coll.find_one({'keyword': keywrod})
    if keyword:
        _id = coll.insert({'keyword': keyword})
    else:
        _id = rz["_id"]
    return _id

def main():
    keyword = 'ワンピース'    
    getItem(keyword)

if __name__ == "__main__":
    main()