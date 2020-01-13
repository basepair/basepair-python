#!/usr/bin/env python2.7
# use basepair interface to create new samples, delete samples
# 
# [2013] - [2014] Basepair LLC
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

# from openpyxl import load_workbook

from interface import BpInterface


def main():
    args = read_args()
    conf = json.load(open(args.config))
    basepair = BpInterface(conf, args.scratch)

    if args.action == 'create-samples':
        create_samples(basepair, args.file)
    elif args.action == 'download-raw':
        download_raw(basepair, args.file)
    elif args.action == 'start-analysis':
        start_analysis(basepair, args.file)
    elif args.action == 'modify-analysis':
        modify_analysis(basepair, args.analysis)
    elif args.action == 'delete-sample':
        delete_sample(basepair, args.sample)


# read info from an excel file and create samples
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
    # wb = load_workbook(filename)
    # ws = wb.worksheets[0]

    # header = [cell.value for cell in ws.rows[0]]
    # for k in xrange(1, ws.max_row):
    for line in open(filename):
        uid = line.strip()

        sample = basepair.get_info('samples', uid)
        keys = [sample['s3path'], sample['s3path_pe']]
        for key in keys:
            if not key:
                continue
            
            filename = '{}-{}/{}'.format(
                    sample['id'], sample['name'].replace(' ', '_'), key.rsplit('/', 1)[1])
            
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
    parser.add_argument('action')
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
