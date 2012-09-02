#!/usr/bin/env python
# coding: utf-8

import tornado.escape
import pycurl, urllib
import StringIO
#import simplejson as json
import time
import pymongo
from pymongo.errors import CollectionInvalid

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

    def ItemSearch(self, genreid, page):
        params = dict(operation="ItemSearch",
                          version = "2010-09-15",
                          page = page,
                          genreId = genreid,)
        msg = self.result(params)
        if msg['Header']['Status'] == 'Success':
            return msg['Body']['ItemSearch']
        else:
            return msg['Header']['StatusMsg']

class GetItem(object):
    """GetItem from rakuten api"""

    @property    
    def db(self):
        """mongodb settings"""
        if not hasattr(GetItem, "_db"):
            _db = pymongo.Connection().bipapa
        return _db
    """
    def getCollId(self, keyword):
        COLLECTION_NAME = "KeywordList"
        try:
            coll = self.db.create_collection(COLLECTION_NAME)
        except CollectionInvalid:
            coll = self.db[COLLECTION_NAME]
        rz = coll.find_one({'keyword': keyword})
        if not rz:
            _id = coll.insert({'keyword': keyword})
        else:
            _id = rz["_id"]
        return _id
    """    
    def getCollList(self):
        try:
            coll = self.db.genreId
        except CollectionInvalid:
            pass
        genreidlist = [ genreid["genreId"] for genreid in coll.find({"genreLevel": 2}) ]
        return genreidlist
                
    def getItem(self, coll_name, page=1):
        """ get item from rakuten api """
        coll = self.db[coll_name]
        getapi = GetAPI()
        itemresult = getapi.ItemSearch(coll_name, page)
        if page < itemresult["pageCount"]:
            for item in itemresult["Items"]["Item"]:
                if not coll.find_one(item["itemCode"]):
                    _item = {}
                    _item["itemName"]       =   item["itemName"]
                    _item["itemImageUrl"]   =   item["mediumImageUrl"].split("?")[0]           
                    _item["itemPrice"]      =   item["itemPrice"]
                    _item["itemCode"]       =   item["itemCode"]
                    _item["genreId"]        =   item["genreId"]
                    _item["itemUrl"]        =   item["itemUrl"]
                    _item["timestamp"]      =   int(time.time())
            
                    _id = coll.insert(_item)
                    print GetImg2db(_id, str(_item["itemImageUrl"]))
            self.getItem(coll_name, page + 1)

def main():
    g = GetItem()
#    keyword = 'ワンピース'
    for coll_name in g.getCollList():
        g.getItem(str(coll_name))

if __name__ == "__main__":
    main()