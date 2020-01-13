#!/usr/bin/env python
'''wrapper for boto AWS SQS'''
from __future__ import print_function

from builtins import object
import sys
# import os
import json
import argparse
import random
# import time

import boto
from boto.sqs.jsonmessage import JSONMessage
import requests


class BpSQS(object):
    '''wrapper for boto AWS SQS'''
    def __init__(self, conf, config_file=None, queue='decider',
                 timeout=120, wait_time=20):
        if config_file:
            self.conf = json.load(open(config_file))
        else:
            self.conf = conf
        self.wait_time = wait_time
        self.q = None

        internet = True
        try:
            requests.get('https://www.google.com/', timeout=1)
        except requests.exceptions.ConnectionError:
            print('warning: no internet', file=sys.stderr)
            internet = False

        if internet:
            self.conn = boto.connect_sqs(
                aws_access_key_id=self.conf['aws']['aws_id'],
                aws_secret_access_key=self.conf['aws']['aws_secret'])

            self.q = self.conn.create_queue(queue, timeout)
            self.q.set_message_class(JSONMessage)

    def send_message(self, _msg):
        '''send message'''
        delay = _msg.get('delay', 0)

        message = JSONMessage()
        message.set_body(_msg)
        status = self.q.write(message, delay_seconds=delay)
        return status

    # {u'ApproximateFirstReceiveTimestamp' '1535158416671',
    # u'SenderId': u'',
    # u'ApproximateReceiveCount': u'1
    # u'SentTimestamp': u'1535158416657'}
    def get_messages(self):
        '''get messages'''
        return self.q.get_messages(
            attributes=['All'],
            num_messages=10,
            wait_time_seconds=self.wait_time)

    def get_message(self):
        '''get a message'''
        return self.q.read(wait_time_seconds=self.wait_time)
        # except socket.gaierror:
        #     print >>sys.stderr, 'no connection, sleeping for a minute'
        #     time.sleep(60)
        #     return None

    def clear(self, wetrun=False):
        '''clear the queue, delete messages'''
        msgs = self.get_messages()
        print(msgs, file=sys.stderr)
        for msg in msgs:
            print(msg, file=sys.stderr)
            if wetrun:
                self.q.delete_message(msg)


def main():
    '''script'''
    args = read_args()
    # test_decider_queue(args)
    # test_instance_queue(args)
    if args.clear:
        sqs = BpSQS(args.config_file)
        sqs.clear(args.wetrun)


def test_decider_queue(args):
    '''test decider queue'''
    sqs = BpSQS(args.config_file)
    msg = {
        "message": "completed",
        "analysis-id": 1481,
        "data": {},
        "sender": "decider"
    }
    sqs.send_message(msg)
    print(json.dumps(msg, indent=2), file=sys.stderr)


def test_instance_queue(args):
    '''test instance queue'''
    analysis_id = int(1000000 * random.random())
    sqs = BpSQS(args.config_file, 'instance', 600)
    msg = {
        'action': 'start-instance',
        'name': 'bp-%s' % analysis_id,
        'kind': 'spot',
        'mode': 'dev',
        'task_list': 'worker',
        'analysis_id': analysis_id,
    }
    sqs.send_message(msg)
    print(json.dumps(msg, indent=2), file=sys.stderr)


def read_args():
    '''user args'''
    parser = argparse.ArgumentParser(description='cmd line instance control')
    parser.add_argument('-c', '--config-file')
    parser.add_argument('-a', '--action')
    parser.set_defaults(
        config_file='setup/config.dev.json'
    )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
