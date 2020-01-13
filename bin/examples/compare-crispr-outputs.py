#!/usr/bin/env python2.7
import argparse
import json
import sys
import subprocess
import tempfile

import basepair


def main():
    args = read_args()
    conf = json.load(open(args.config))
    bp = basepair.connect(conf)

    # get all analyses for the user
    analyses = bp.get_analyses()
    # keep the one using CRISPR workflow
    analyses = filter(lambda x: x['workflow'] == '/api/v1/workflows/14',
                      analyses)
    # get the detailed info, which includes output files
    analyses = [bp.get_analysis(a['id']) for a in analyses]

    count_total, count_same = 0, 0
    for analysis in analyses:
        # find txt output files, if # less than 2, continue
        outfiles = bp.filter_files_by_tags(
            analysis['files'], tags=['parsed', 'txt'], multiple=True)
        if not outfiles or len(outfiles) < 2:
            continue

        # download the 2 files and diff. if retval == 0, files same
        try:
            file1 = bp.download_file(outfiles[0]['path'])
            file2 = bp.download_file(outfiles[1]['path'])
            cmd = 'bash -c "diff <(tail +2 {}) <(tail +2 {})"'.format(
                file1, file2)
            temp = tempfile.TemporaryFile()
            retval = subprocess.call(cmd, shell=True, stdout=temp)
            temp.seek(0)
            stdout = temp.read()
            temp.close()
        except:
            print >>sys.stderr, 'warning: error for ', analysis['name']
            continue

        count_total += 1
        if retval == 0:
            count_same += 1
        else:
            print analysis['name']
            print stdout
            print

    print >>sys.stderr, 'For {}/{} analysis, output files match perfectly\
        '.format(count_same, count_total)


def read_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--config', help='')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
