#!/usr/bin/env python
# coding: utf-8

from pymongo import Connection
from pymongo.errors import CollectionInvalid
from rakuten_api import rakuten_api

def genreIdGet(genreId):
    msg = rakuten_api(operation="GenreSearch",
                      version = "2007-04-11",
                      genreId = genreId)
    genreid_list = []
    if msg['Header']['Status'] == 'Success':
        for ch in msg['Body']['GenreSearch']['child']:
             genreid_list.append(ch)
    return genreid_list

def mainGenreId(genreid_list):
    for genreid in genreid_list:
        if not mongo_coll.find_one(genreid):
            mongo_coll.insert(genreid)
            genreidArray = nextGenreId(genreid["genreId"])
            if len(genreidArray):
                mainGenreId(genreidArray)

def nextGenreId(genreid):
    genreidarray = genreIdGet(genreid)
    return genreidarray

def initGenreId():
    '''
    100371	レディースファッション
    216129	ジュエリー・アクセサリー   
    '''
    init_genreid_list = [100371, 216129]
    for genreid in init_genreid_list:
        topGenreId = genreIdGet(genreid)
        mainGenreId(topGenreId)

def main():
    initGenreId()

if __name__ == "__main__":
    DB_NAME = 'bipapa'
    COLLECTION_NAME = 'genreId'
    mongo_conn = Connection()
    mongo_db = mongo_conn[DB_NAME]

    try:
        mongo_coll = mongo_db.create_collection(COLLECTION_NAME)
    except CollectionInvalid:
        mongo_coll = mongo_db[COLLECTION_NAME]
    main()
