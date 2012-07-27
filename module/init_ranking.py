#!/usr/bin/env python
# coding: utf-8

from pymongo import Connection
from pymongo.errors import CollectionInvalid
from rakuten_api import rakuten_api

def rankingGet(genreId):
    msg = rakuten_api(operation="ItemRanking",
                      version = "2010-08-05",
#                      sex = "1",
#                      age = "20",
                      genreId = genreId)
    if msg['Header']['Status'] == 'Success':
        return msg['Body']['ItemRanking']['Items']['Item']
    else:
        print msg['Header']['StatusMsg']

def genreIdList():
    COLLECTION_NAME = 'genreId'
    mongo_conn = Connection()
    mongo_db = mongo_conn[DB_NAME]
    try:
        mongo_coll = mongo_db.create_collection(COLLECTION_NAME)
    except CollectionInvalid:
        mongo_coll = mongo_db[COLLECTION_NAME]
    return  mongo_coll.find({"genreLevel" : 2})

def main():
    genreid_list = genreIdList()
    if genreid_list:
        for genreid in genreid_list:
            items_list = rankingGet(genreid)
            items_keys = ["itemName", "mediumImageUrl", "itemPrice", "genreId", "itemUrl"]
            for items in items_list:
                data = dict([(key,items.pop(key)) for key in items_keys])
                if not mongo_coll.find_one(data):
                    mongo_coll.insert(data)
        #        mongo_coll.insert(dict([(key,items.pop(key)) for key in items_keys]))
        #    mongo_coll.insert(items_dict)
        #    items_dict = {}
        #        for item in msg['Body']['ItemRanking']['Items']['Item']:
        #             items_list.append(item)
        #             items_dict.update(dict([(k,item.pop(k)) for k in items_keys]))
        #             mongo_coll.insert(items)

if __name__ == "__main__":
    DB_NAME = 'bipapa'
    COLLECTION_NAME = 'ranking'
    mongo_conn = Connection()
    mongo_db = mongo_conn[DB_NAME]
    try:
        mongo_coll = mongo_db.create_collection(COLLECTION_NAME)
    except CollectionInvalid:
        mongo_coll = mongo_db[COLLECTION_NAME]

    main()
