#!/usr/bin/env python

from builtins import object
import argparse
import json

import boto
from boto.s3.key import Key


class BpS3(object):
    def __init__(self, conf):
        self.conf = conf

        region = None
        try:
            for reg in boto.sqs.regions():
                if reg.name == self.conf['aws']['s3']['region']:
                    region = reg
                    break
        except KeyError:
            region = None

        self.conn = boto.connect_s3(
            aws_access_key_id=self.conf['aws']['aws_id'],
            aws_secret_access_key=self.conf['aws']['aws_secret'],
            region=region,
        )

    def save_data(self, data, bucket_name, key_name):
        bucket = self.conn.create_bucket(
            bucket_name, location=boto.s3.connection.Location.DEFAULT)
        k = Key(bucket)
        k.key = key_name
        k.set_contents_from_string(json.dumps(data, indent=2))

    # TODO: URL valid for 1 year
    # generate s3 path
    def get_s3_url(self, path, expires_in=None):
        if not expires_in:
            expires_in = 3600 * 24 * 365

        bucket = self.conn.get_bucket(self.conf['aws']['s3']['bucket'])
        key = bucket.get_key(path)
        url = key.generate_url(expires_in) if key else ''

        return url


def main():
    args = read_args()
    conf = json.load(open(args.config_file))
    s3 = BpS3(conf)

    data = {
        'abc': 'def',
        'rst': 'xyz',
    }
    bucket_name = 'bpdev0'
    key_name = 'analysis/1890/__private__/workflow.json'
    s3.save_data(data, bucket_name, key_name)


def read_args():
    parser = argparse.ArgumentParser(description='cmd line instance control')
    parser.add_argument('-c', '--config-file')
    parser.set_defaults(
        config_file='setup/config.dev.json'
    )

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
