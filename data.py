from pymongo import MongoClient
from collections import defaultdict
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


def get_number_of_metrics_per_country(db):
    pipeline = [
        {'$unwind': '$results'},
        {'$project': {
            '_id':0,
            'results.probe_cc': 1,
            'results.success': 1
        }}
    ]
    rs = defaultdict(lambda: defaultdict(int))
    for d in db.ooni_public.aggregate(pipeline):
        if d['results']['success']:
            rs[d['results']['probe_cc']]['successfulBridgeConnections'] += 1
        else:
            rs[d['results']['probe_cc']]['failedBridgeConnections'] += 1
    return rs


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