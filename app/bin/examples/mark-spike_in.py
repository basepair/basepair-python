#!/usr/bin/env python
# mark a sample as spike in

import argparse
import json
import sys

import basepair


def main():
    args = read_args()
    conf = json.load(open(args.config))
    bp = basepair.connect(conf)

    sample = bp.get_sample(args.sample)
    if not sample:
        print >>sys.stderr, 'sample', args.sample, 'not found'
        return

    info = {} if sample['info'] is None else sample['info']
    info.update({
        'spike_in': 'ercc'
    })
    data = {
        'info': info
    }

    res = bp.update_sample(args.sample, data)
    print >>sys.stderr, json.dumps(data, indent=2)
    print res.status_code


def read_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--config')
    parser.add_argument('-s', '--sample')
    parser.set_defaults(
    )

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
