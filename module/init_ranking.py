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
    return  mongo_coll.find({'genreLevel': 2},{"genreId": 1,"_id": 0})

def main():
    genreid_list = genreIdList()
#    genreid_list = [{"genreId": "110729"}]
#    genreid_list = [{"genreId": "100380"}]
    if genreid_list:
        items_keys = ["itemName", "mediumImageUrl", "itemPrice", "genreId", "itemUrl"]
        for genreid in genreid_list:
            items_list =  rankingGet(genreid["genreId"])
            print len(items_list)
            if items_list:
                COLLECTION_NAME = 'ranking' + str(genreid["genreId"])
                mongo_conn = Connection()
                mongo_db = mongo_conn[DB_NAME]
                try:
                    mongo_coll = mongo_db.create_collection(COLLECTION_NAME)
                except CollectionInvalid:
                    mongo_coll = mongo_db[COLLECTION_NAME]
                for items in items_list:
                    data = dict([(key,items.pop(key)) for key in items_keys])
                    data["ImageUrl"] = data.pop("mediumImageUrl").split("?")[0]
            #        print data
                    if not mongo_coll.find_one(data):
                        mongo_coll.insert(data)

if __name__ == "__main__":
    DB_NAME = 'bipapa'
    main()
