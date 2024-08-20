#!/usr/bin/env python

import argparse
import json
import os

from basepair.interface import BpInterface


def main():
    args = read_args()
    conf = json.load(open(os.path.expanduser(args.config)))
    basepair = BpInterface(conf, args.scratch, use_cache=(not args.no_cache))

    # sample = basepair.get_sample(15)
    sample = basepair.get_sample(12)
    # for a in sample['analyses_full']:
    #     print a['name']
    # print

    filepath = basepair.get_expression_count_file(sample)
    # filepath = basepair.get_tdf_file(sample)

    print filepath


def read_args():
    parser = argparse.ArgumentParser(description='Basepair API')
    parser.add_argument('-c', '--config')
    parser.add_argument('-s', '--scratch')
    parser.add_argument('--no-cache', action='store_true')

    parser.set_defaults(
            config='~/basepair/bioinformatics/api/config/config.utk.json',
            scratch='~/scratch/users/tags',
            no_cache=False,
            )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
