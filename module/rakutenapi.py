#!/usr/bin/env python
# coding: utf-8

import tornado.escape
import pycurl
import StringIO

class RakutenAPI(object):
    def __init__(self):
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.FOLLOWLOCATION, 1)
        self.c.setopt(pycurl.MAXREDIRS, 5)
         
    def result(self, parts):
        host = "http://api.rakuten.co.jp/rws/3.0/json?"
        developerid = "developerId=375ecf0e10025bd1489adffb9c51c018"
#        url = host + developerid + '&' + parts
        url = "".join([host, developerid ,'&', parts])
        self.c.setopt(pycurl.URL, url)
        b = StringIO.StringIO()
        self.c.setopt(pycurl.WRITEFUNCTION, b.write)
        self.c.perform()
        response = b.getvalue()
        result = tornado.escape.json_decode(response)
        return result

class GetAPI(RakutenAPI):
    def rankingGet(self, genreid=110729):
        search_dict = dict(operation="ItemRanking",
                          version = "2010-08-05",
                          genreId = genreid)
        parts = '&'.join(['%s=%s' % (key, value) for key, value in search_dict.iteritems()])
        msg = self.result(parts)
        print msg
        if msg['Header']['Status'] == 'Success':
            return msg['Body']['ItemRanking']['Items']['Item']
        else:
            print msg['Header']['StatusMsg']

def main():
    x = GetAPI()
    x.rankingGet()
#    print x.genreidGet()

if __name__ == "__main__":
    main()
