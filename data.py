from pymongo import MongoClient
from bson.code import Code
from pprint import pprint

collection = 'ooni_public'


def get_distinct_asns(db):
    """
    Returns a list of anonymous systems from which bridge_reachability tests have been performed
    :param collection:
    :return:
    """
    return db[collection].distinct('probe_asn')


def get_country_names(db):
    pipeline = [
        {'$unwind': '$results'},
        {'$group': {"_id": "$probe_cc", "probe_cc": {"$sum": 1}}},
        {'$sort': {'count': -1}},
    ]
    return list(db.ooni_public.aggregate(pipeline))


def get_mongodb_connection(host, port):
    """
    Initiates a connection to the remote MongoDB server
    :param host: host of the server we want to connect to
    :param port: port of the MongoDB instance
    :return:
    """
    print("Initiating MongoDB connection to %s:%d" % (host, port))
    client = MongoClient(host, port)
    return client.ooni


if __name__ == "__main__":
    db = get_mongodb_connection(host='buildstuffwith.me', port=27017)
    pprint(get_country_names(db))
