#!/usr/bin/env python3
from boto.s3.connection import S3Connection
from pymongo import MongoClient
from pprint import pprint
import requests
import boto3
import json
import zlib
import yaml
import os

host = 'buildstuffwith.me'
port = 27017

AWS_KEY = 'AKIAICLIHHE7CXMFVGDA'
AWS_SECRET_KEY = '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'

def main():
    with open('reports.json') as reports:
        reports = json.load(reports)

    # Cache a list of S3 object keys
    s3 = S3Connection(AWS_KEY, AWS_SECRET_KEY)
    bucket = s3.get_bucket('ooni-public')
    keys = set()
    for object in bucket.list():
        if 'bridge_reachability' in object.name:
            keys.add(object.name)
    print("Cached %d key names" % (len(keys)))

    connection = MongoClient(host=host, port=port)
    db = connection.ooni.ooni_public

    for report in reports:
        if 'bridge_reachability' not in report['test_name']:
            continue
        r = {
            'id': report['id'],
            'backend_version': report['backend_version'],
            'data_format_version': report['data_format_version'],
            'input_hashes': report['input_hashes'],
            'probe_cc': report['probe_cc'],
            'probe_asn': report['probe_asn'],
            'probe_ip': report['probe_ip'],
            'report_filename': report['report_filename'],
            'software_name': report['software_name'],
            'software_version': report['software_version'],
            'start_time': report['start_time'],
            'test_name': report['test_name'],
            'test_helpers': report['test_helpers'],
            'test_version': report['test_version'],
            'options': report['options']
        }
        fetch_yaml_report(s3=s3, bucket=bucket, filename=report['report_filename'], keys=keys)
        pprint(r)
        break
    else:
        connection.close()


def fetch_yaml_report(s3, bucket, filename, keys):
    print("Fetching %s" % (filename))
    basename = filename.replace('.yaml', '.yaml.gz')
    for key in keys:
        if key.endswith(basename):
            k = bucket.get_key(key)
            gzipped_yaml = k.get_contents_as_string()

            # Decompress YAMLOO and convert to JSON
            reports = yaml.safe_load_all(zlib.decompress(bytes(gzipped_yaml), 15+32))
            for report in reports:
                print(report)


if __name__ == "__main__":
    main()
