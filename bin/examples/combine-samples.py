#!/usr/bin/env python2.7
# use basepair interface to create new samples, delete samples
# 
# [2013] - [2015] Basepair LLC
#   All Rights Reserved.
# 
#  NOTICE:  All information contained herein is, and remains
#  the property of Basepair LLC and its suppliers,
#  if any.  The intellectual and technical concepts contained
#  herein are proprietary to Basepair LLC
#  and its suppliers and may be covered by U.S. and Foreign Patents,
#  patents in process, and are protected by trade secret or copyright law.
#  Dissemination of this information or reproduction of this material
#  is strictly forbidden unless prior written permission is obtained
#  from Basepair LLC.

import argparse
import json
import sys
import os

from interface import BpInterface


def main():
    args = read_args()
    conf = json.load(open(args.config))
    bp = BpInterface(conf, args.scratch)

    data = [
            ['Unt-1', [781, 782, 783, 784]],
            ['Unt-2', [785, 786, 787, 789]],
            ['Unt-3', [791, 792, 793, 794]],
            ['Unt-1-Inp1', [795, 796, 797, 798]],
            ['Unt-1-Inp2', [799, 800, 801, 802]],
            ['Unt-1-Inp3', [803, 804, 805, 806]],
            ['LPS-1', [807, 808, 809, 810]],
            ['LPS-2', [811, 812, 813, 814]],
            ['LPS-3', [815, 816, 817, 818]],
            ['LPS-Input1', [819, 820, 821, 822]],
            ['LPS-Input2', [823, 824, 825, 826]],
            ['LPS-Input3', [827, 828, 829, 830]],
            ['IgG-1', [831, 832, 833, 834]],
            ['IgG-2', [835, 836, 837, 838]],
            ['IgG-3', [839, 840, 841, 842]],
            ]

    for name, ids in data:
        files = []
        print name
        sample = None
        for uid in ids:
            sample = bp.get_sample(uid)
            print '\t', sample['s3path']
            filename = 'fq/{}'.format(os.path.basename(sample['s3path']))
            # print '\t', filename
            filepath = bp.get_file(sample['s3path'], filename)
            files.append(filename)
        print
        # print files
        # continue
        files2 = [f.replace('_L001_', '_L000_').
                replace('_L002_', '_L000_').
                replace('_L003_', '_L000_').
                replace('_L004_', '_L000_') for f in files]
        prefix = os.path.commonprefix(files2)
        # print prefix
        cmd1 = 'gzcat {} | gzip > {}'.format(' '.join(files), prefix)
        # print
        print cmd1
        # import ipdb; ipdb.set_trace()
        # retval = os.system(cmd1)
        data =  {
                'name': name,
                'genome': sample['genome'],
                'datatype': sample['datatype'],
                'platform': sample['platform'],
                'rate': 15,
                'avg_fragment_length': 400,
                'default_workflow': 5,
                'filepath1': prefix,
                # 'owner': 16,
                }
        sample_id = bp.create_sample(data, upload=True)
        # break


def create_samples(basepair, filename):
    wb = load_workbook(filename)
    ws = wb.get_sheet_by_name('Sheet1')

    header = [cell.value for cell in ws.rows[0]]
    for k in xrange(1, ws.max_row):
        vals = [cell.value for cell in ws.rows[k]]
        rec = dict(zip(header, vals))

        data = {
                'name': rec['Name'],
                'genome': rec['Genome'],
                'datatype': rec['Data type'],
                }

        # # existing record, skip
        if rec['Sample Id']:
            # continue
            data['id'] = rec['Sample Id']

        if 'Workflow' in rec:
            data['default_workflow'] = rec['Workflow']
        if 'Platform' in rec:
            data['platform'] = rec['Platform']
        if 'Filepath 1' in rec:
            data['filepath1'] = rec['Filepath 1']
        if 'Filepath 2' in rec:
            data['filepath2'] = rec['Filepath 2']
        if 'S3path' in rec:
            data['s3path'] = rec['S3path']
        if 'S3path_pe' in rec:
            data['s3path_pe'] = rec['S3path_pe']

        sample_id = basepair.create_sample(data, upload=False)
        ws.rows[k][0].value = sample_id

        # break
    
    wb.save(filename)


# read info from an excel file and create samples
def download_raw(basepair, filename):
    wb = load_workbook(filename)
    ws = wb.worksheets[0]

    header = [cell.value for cell in ws.rows[0]]
    for k in xrange(1, ws.max_row):
        vals = [cell.value for cell in ws.rows[k]]
        rec = dict(zip(header, vals))

        sample = basepair.get_info('samples', rec['Id'])
        keys = [sample['s3path'], sample['s3path_pe']]
        for key in keys:
            if not key:
                continue
            
            filename = '{}-{}/{}'.format(
                    rec['Id'], rec['Name'].replace(' ', '_'), key.rsplit('/', 1)[1])
            
            basepair.get_file(key, filename)


# read info from an excel file and create samples
def start_analysis(basepair, filename):
    wb = load_workbook(filename)
    ws = wb.get_sheet_by_name('Sheet1')

    header = [cell.value for cell in ws.rows[0]]
    for k in xrange(1, ws.max_row):
        vals = [cell.value for cell in ws.rows[k]]
        rec = dict(zip(header, vals))

        if rec['Analysis Id']:
            continue

        sample_id = int(rec['Sample Id'])
        workflow_id = int(rec['Workflow'])

        analysis_id = basepair.create_analysis(workflow=workflow_id, sample=sample_id)
        ws.rows[k][1].value = analysis_id

        # break
    
    wb.save(filename)


# def create_analysis(basepair, workflow, sample, control=None):
#     if not control:
#         basepair.create_analysis(workflow=workflow, sample=sample)
#     else:
#         basepair.create_analysis(workflow=workflow, sample=sample, control=control)


def modify_analysis(basepair, analysis_id, data=None):
    data = {
            'name': 'new name'
            }
    basepair.modify_analysis(analysis_id, data)


def delete_sample(basepair, sample_id):
    basepair.delete_sample(sample_id)


def read_args():
    parser = argparse.ArgumentParser(description='Basepair API')
    parser.add_argument('--config')
    parser.add_argument('--scratch')
    parser.add_argument('-f', '--file')
    parser.add_argument('-s', '--sample', type=int)
    parser.add_argument('-c', '--control', type=int)
    parser.add_argument('-w', '--workflow', type=int)
    parser.add_argument('-a', '--analysis', type=int)

    parser.set_defaults(
            config='api/utk.config.json',
            )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
