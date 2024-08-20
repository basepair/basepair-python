#!/usr/bin/env python2.7
# use basepair interface to create new samples, delete samples
# 
# [2015] - [2018] Basepair INC
#   All Rights Reserved.
# 
#  NOTICE:  All information contained herein is, and remains
#  the property of Basepair INC and its suppliers,
#  if any.  The intellectual and technical concepts contained
#  herein are proprietary to Basepair INC
#  and its suppliers and may be covered by U.S. and Foreign Patents,
#  patents in process, and are protected by trade secret or copyright law.
#  Dissemination of this information or reproduction of this material
#  is strictly forbidden unless prior written permission is obtained
#  from Basepair INC.

import argparse
import json
import sys

import basepair
import requests


def main():
    args = read_args()

    url = 'http://127.0.0.1/api/v1/samples'
    data = {
        'name': 'samp'
    }
    payload = {
        'username': 'test@basepair.com',
        'api_key': '1b2635d03752d799584680bd98759c88ca391072'
    }
    payload = {
        'username': 'utk',
        'api_key': '8eaa2ec42be5f0f7c4c7e0c07838d73b1eed60ac'
    }
    headers = {
        'content-type': 'application/json'
    }
    # data.update(payload)
    res = requests.post(
        url, data=json.dumps(data), params=payload, headers=headers)
        # url, data=json.dumps(data), headers=headers)
    # import ipdb; ipdb.set_trace()
    print res


def using_api():
    conf = json.load(open(args.config))
    bp = basepair.connect(conf)

    data = {
        "name": "Sample 10",
        "genome": "hg19",
        "datatype": "dna-seq",
        "file1": "/path/to/file1.fastq.gz",
        "file2": "/path/to/file2.fastq.gz",
    }
    sample_id = bp.create_sample(data)
    print sample_id, data['name']


def read_args():
    parser = argparse.ArgumentParser(description='Basepair API')
    parser.add_argument('--config')
    # parser.add_argument('--scratch')

    parser.set_defaults(
            )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
