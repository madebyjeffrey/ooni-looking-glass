from pymongo import MongoClient
from collections import defaultdict
from bson.code import Code
from pprint import pprint
import numpy as np
import pandas as pd
import pycountry
import requests

collection = 'ooni_public'


def autodict():
    l = lambda: defaultdict(l)
    return l()

def get_link_to_censorship_report(cc):
    country_name = pycountry.countries.get(alpha2=cc).name.lower()
    url = 'https://opennet.net/countries/%s' % country_name
    response = requests.head(url)
    if response.status_code == 200:
        return url
    else
        return "#"

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


def get_pluggable_transports(db):
    return db.ooni_public.distinct('results.transport_name')

def get_pluggable_transport_metrics_per_country_as_table(db):
    metrics = pd.DataFrame(get_pluggable_transport_metrics_per_country(db))
    for cc in metrics:
        for transport in metrics[cc].keys():
           successful = metrics[cc][transport]['successfulBridgeConnections']
           failures = metrics[cc][transport]['failedBridgeConnections']
           try:
                metrics[cc][transport]['failureRate'] = (failures / (successful + failures)) * 100
           except ZeroDivisionError:
                metrics[cc][transport]['failureRate'] = 0
    return metrics


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
    # Pre-populate the return table to prevent empty values for countries/pluggable transports
    rs = {}
    for cc in get_country_codes(db=db):
        rs[cc] = defaultdict(lambda: defaultdict(int))
        for transport in get_pluggable_transports(db=db):
            rs[cc][transport]['successfulBridgeConnections'] = 0
            rs[cc][transport]['failedBridgeConnections'] = 0
    for d in db.ooni_public.aggregate(pipeline):
        d = d['results']
        if len(d) != 3:
            continue
        if d['success']:
            rs[d['probe_cc']][d['transport_name']]['successfulBridgeConnections'] += 1
        else:
            rs[d['probe_cc']][d['transport_name']]['failedBridgeConnections'] += 1
    return rs


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