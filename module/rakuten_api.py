#!/usr/bin/env python
# coding: utf-8

import tornado.escape
import pycurl
import StringIO

def rakuten_api(**parts):
    host = "http://api.rakuten.co.jp/rws/3.0/json?"
    search_dict = {"developerId" : "375ecf0e10025bd1489adffb9c51c018"}
    search_dict.update(parts)
    search_list = []
    for key, value in search_dict.iteritems():
        temp = '%s=%s' % (key, value)
        search_list.append(temp)
    url = host + '&'.join(search_list)
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    b = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.perform()
    response = b.getvalue()
    api_result = tornado.escape.json_decode(response)
    return api_result
