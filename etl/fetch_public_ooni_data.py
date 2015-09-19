#!/usr/bin/env python3
from boto.s3.connection import S3Connection
from pymongo import MongoClient
from pprint import pprint
import json
import zlib
import yaml

host = 'buildstuffwith.me'
port = 27017

AWS_KEY = 'AKIAICLIHHE7CXMFVGDA'
AWS_SECRET_KEY = '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'


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


def get_s3_bucket_connection(bucket_name):
    """
    Returns an instance of a connector to a given AWS S3 bucket
    :param bucket:
    :return:
    """
    print("Connecting to s3://%s" % (bucket_name))
    s3 = S3Connection(AWS_KEY, AWS_SECRET_KEY)
    bucket = s3.get_bucket(bucket_name)
    return bucket


def get_bridge_reachability_report_keys(s3):
    """
    Returns keys associated with bridge reachability reports
    :param bucket:
    :return:
    """
    keys = set()
    print("Getting s3 bucket keys")
    for key in s3.list():
        if 'bridge_reachability' in key.name:
            keys.add(key.name)
    return keys


def get_bridge_reachability_reports(s3):
    """
    Fetches Tor bridge reachability reports from AWS S3
    :param s3:
    :param debug:
    :return:
    """
    reports = []
    keys = get_bridge_reachability_report_keys(s3=s3)

    for i, key in enumerate(keys):
        print("[%d/%d] %s" % (i+1, len(keys), key))

        gzipped_yml = s3.get_key(key).get_contents_as_string()
        yml = list(yaml.safe_load_all(zlib.decompress(bytes(gzipped_yml), 15+32)))

        # Parse YAML file into header/payload, and associated payload with header
        header = yml[0]
        report = header
        report['results'] = []

        for subreport in yml[1:]:
            if subreport['record_type'] == 'entry':
                print("subreport")
                report['results'].append(subreport)
            if subreport['record_type'] == 'footer':
                report['footer'] = subreport
        reports.append(report)
    return reports


def insert_bridge_reachability_reports(db, reports):
    """
    Inserts bridge reachability reports into MongoDB
    :param db: instance of MongoDB to insert data into
    :param reports: collection of reports to insert
    :return:
    """
    print("Inserting data into MongoDB")
    db.ooni_public.insert_many(reports)


def main():
    db = get_mongodb_connection(host='buildstuffwith.me', port=port)
    bucket = get_s3_bucket_connection(bucket_name='ooni-public')
    reports = get_bridge_reachability_reports(s3=bucket)
    insert_bridge_reachability_reports(db=db, reports=reports)

if __name__ == "__main__":
    main()
