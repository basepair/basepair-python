#!/usr/bin/env python
import argparse
import basepair
import json
import os
import sys

sratoolkit = '~/apps/sratoolkit/sratoolkit.2.3.5-2-centos_linux64/bin'
fastq_dump = sratoolkit + '/fastq-dump'
cache_mgr = sratoolkit + '/cache-mgr'


def main():
    args = read_args()
    conf = json.load(open(args.config))
    # conf['api']['username'] = 'tristandemooij'
    # conf['api']['api_key'] = 'c9df8a196b09be55f8720fcab9103794aea839d3'
    bp = basepair.connect(conf, verbose=False)

    fastq = '{} --split-files {} --outdir . '
    # data = [
    #     [7667, 'uploads/963/5585/SRR1222686_2.fastq'],
    #     [7666, 'uploads/963/5585/SRR1222686_1.fastqu'],
    #     [7669, 'uploads/963/5586/SRR1222685_2.fastq.gz'],
    #     [7668, 'uploads/963/5586/SRR1222685_1.fastq'],
    #     [7671, 'uploads/963/5587/SRR1222684_2.fastq.gz'],
    #     [7670, 'uploads/963/5587/SRR1222684_1.fastq.gz'],
    #     [7673, 'uploads/963/5588/SRR1222682_2.fastq.gz'],
    #     [7672, 'uploads/963/5588/SRR1222682_1.fastq.gz'],
    #     [7675, 'uploads/963/5589/SRR1222680_2.fastq.gz'],
    #     [7674, 'uploads/963/5589/SRR1222680_1.fastq.gz'],
    #     [7677, 'uploads/963/5590/SRR1222678_2.fastq.gz'],
    #     [7676, 'uploads/963/5590/SRR1222678_1.fastq.gz'],
    #     [7679, 'uploads/963/5591/SRR1222677_2.fastq.gz'],
    #     [7678, 'uploads/963/5591/SRR1222677_1.fastq.gz'],
    samples = [
        5585,
        5586,
        5587,
        5588,
        5589,
        5590,
        5591,
    ]
    samples.reverse()

    # for sample_id in samples:
    sample = bp.get_sample(args.sample)
    srr = sample['uploads'][0]['key'].split('/')[3][:10]
    prefix = sample['uploads'][0]['key'].rsplit('/', 1)[0]
    upload_1 = sample['uploads'][0]
    upload_2 = sample['uploads'][1]
    if upload_1['is_paired_end']:
        upload_1, upload_2 = upload_2, upload_1

    print >>sys.stderr, sample['name']
    if not args.dryrun:
        bp.update_upload(upload_1['id'], {'status': 'in_progress'})
        bp.update_upload(upload_2['id'], {'status': 'in_progress'})

    # get fastq files
    cmd = fastq.format(fastq_dump, srr)
    print >>sys.stderr, '\t', 'getting data'
    print >>sys.stderr, '\t', cmd
    if args.dryrun:
        return
    os.system(cmd)

    # copy file and update record
    print >>sys.stderr, '\tupload file 1'
    filename = srr + '_1.fastq'
    os.system('aws s3 cp {} s3://basepair/{}/'.format(filename, prefix))
    data = {
        'key': prefix + '/' + filename,
        'filesize': os.stat(filename).st_size,
        'status': 'completed',
        'seq_length': 0,
    }
    bp.update_upload(upload_1['id'], data)

    print >>sys.stderr, '\tupload file 2'
    filename = srr + '_2.fastq'
    os.system('aws s3 cp {} s3://basepair/{}/'.format(filename, prefix))
    data = {
        'key': prefix + '/' + filename,
        'filesize': os.stat(filename).st_size,
        'status': 'completed',
        'seq_length': 0,
    }
    bp.update_upload(upload_2['id'], data)

    # os.system('{} --clear'.format(cache_mgr))
    # os.system('rm {}*fastq'.format(srr))
    print >>sys.stderr


def read_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--config', help='')
    parser.add_argument('-s', '--sample', help='')
    parser.add_argument('-d', '--dryrun', action='store_true')
    parser.set_defaults(
        # config='/home/ec2-user/logs/config.prod.json',
        config='config.tristan.json',
    )

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
