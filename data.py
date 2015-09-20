from pymongo import MongoClient
from collections import defaultdict
from bson.code import Code
from pprint import pprint
import pandas as pd

collection = 'ooni_public'

def autodict():
    l = lambda: defaultdict(l)
    return l()


def defaultdict_to_dict(d):
    if isinstance(d, defaultdict):
        d = {k: defaultdict_to_dict(v) for k, v in d.iteritems()}
    return d


def get_distinct_asns(db):
    """
    Returns a list of anonymous systems from which bridge_reachability tests have been performed
    :param collection:
    :return:
    """
    return db[collection].distinct('probe_asn')


def get_country_codes(db):
    return db.ooni_public.distinct('probe_cc')


def get_pluggable_transport_metrics_per_country_as_table(db):
    metrics = get_pluggable_transport_metrics_per_country(db=db)
    user_ids = []
    frames = []
    for user_id, d in metrics.items():
        user_ids.append(user_id)
        frames.append(pd.DataFrame.from_dict(d, orient='index'))
    df = pd.concat(frames, keys=user_ids)
    return df


def get_pluggable_transport_metrics_per_country(db):
    pipeline = [
        {'$unwind': '$results'},
        {'$project': {
            '_id': 0,
            'results.probe_cc': 1,
            'results.success': 1,
            'results.transport_name': 1,
        }}
    ]
    rs = {}
    for cc in get_country_codes(db=db):
        rs[cc] = defaultdict(lambda: defaultdict(int))
    for d in db.ooni_public.aggregate(pipeline):
        d = d['results']
        if len(d) != 3:
            continue
        if d['success']:
            rs[d['probe_cc']][d['transport_name']]['successfulBridgeConnections'] += 1
        else:
            rs[d['probe_cc']][d['transport_name']]['failedBridgeConnections'] += 1
    return defaultdict_to_dict(rs)


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


if __name__ == "__main__":
    db = get_mongodb_connection(host='buildstuffwith.me', port=27017)
    metrics = get_pluggable_transport_metrics_per_country_as_table(db=db)
    pprint(metrics)