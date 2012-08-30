#!/usr/bin/env python
# coding: utf-8

import tornado.escape
import pycurl, urllib
import StringIO
#import simplejson as json
import time

from getimg2db import GetImg2db

class RakutenAPI(object):
#    def __init__(self):
#        self.c = pycurl.Curl()
#        self.c.setopt(pycurl.FOLLOWLOCATION, 1)
#        self.c.setopt(pycurl.MAXREDIRS, 5)
#        self.c.setopt(pycurl.URL, 'http://api.rakuten.co.jp/rws/3.0/json?')
#        self.c.setopt(pycurl.TIMEOUT, 30)
#        self.c.setopt(pycurl.POST, 1)
         
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
#    @property
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

#    @property
    def ItemSearch(self, keyword, page=1):
        params = dict(operation="ItemSearch",
                          version = "2010-09-15",
                          page = page,
                          keyword = keyword,)
        msg = self.result(params)
        if msg['Header']['Status'] == 'Success':
            return msg['Body']['ItemSearch']
        else:
            return msg['Header']['StatusMsg']
    
def main():
    x = GetAPI()
    keyword = 'ワンピース'
#    print x.ItemRanking(100372)
    res = x.ItemSearch(keyword)
    if res:
        pageCount = int(res["pageCount"]) + 1
        for page in range(2,pageCount):
#            print "keyword is %s ,page is %s" % (keyword, page)
            res = x.ItemSearch(keyword,page)

if __name__ == "__main__":
    main()
