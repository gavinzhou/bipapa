#!/usr/bin/env python
# coding: utf-8

import pycurl
#import StringIO

def GetImg(filename, url):
    crl = pycurl.Curl()
    crl.setopt(pycurl.HTTPGET, 1)
    crl.setopt(pycurl.URL, url)
    outfile = open("./tmp/" + filename + ".jpg" ,"wb")
    crl.setopt(pycurl.WRITEFUNCTION, outfile.write)
    crl.perform()

#url = "http://thumbnail.image.rakuten.co.jp/@0_mall/pierrot/cabinet/img14/a1203-031544_1.jpg"
#filename = "a1203-031544_1.jpg"

#GetImg(filename, url)
