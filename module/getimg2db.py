#!/usr/bin/env python
# coding: utf-8

import pycurl
import StringIO

from pymongo import Connection
from gridfs import GridFS

def img2db(img, content_type, filename):
    db = Connection().gridfs
    fs = GridFS(db)
    oid = fs.put(img, content_type = content_type, filename = filename)
    return oid

def GetImg2db(filename, url):
    crl = pycurl.Curl()
    crl.setopt(pycurl.HTTPGET, 1)
    crl.setopt(pycurl.URL, url)
    data = StringIO.StringIO()
#    outfile = open("./tmp/" + filename + ".jpg" ,"wb")
    crl.setopt(pycurl.WRITEFUNCTION, data.write)
    crl.perform()
    img = data.getvalue()
    content_type = crl.getinfo(pycurl.CONTENT_TYPE)
    oid = img2db(img, content_type, filename)
    return  oid

#url = "http://thumbnail.image.rakuten.co.jp/@0_mall/pierrot/cabinet/img14/a1203-031544_1.jpg"
#filename = "501a460c41ab101fda561b23"

#print GetImg(filename, url)