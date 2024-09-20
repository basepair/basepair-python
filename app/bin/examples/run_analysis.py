#!/usr/bin/env python2.7
# use basepair API to run analysis

# parallel ./run_analysis.py ::: $(seq 1 50)

import argparse
import sys
import json

import basepair


def main():
    args = read_args()
    bp = basepair.connect(json.load(open(args.config)))

    analysis_id = bp.create_analysis(sample_id=1, workflow_id=10)
    print >>sys.stderr, 'Created analysis', analysis_id


def read_args():
    parser = argparse.ArgumentParser(description='Basepair API')
    parser.add_argument('num')
    parser.add_argument('--config')

    parser.set_defaults(
        config='/Users/amit/Downloads/conf.json',
    )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
