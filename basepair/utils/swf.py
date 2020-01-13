#!/usr/bin/env python

from __future__ import print_function
from builtins import object
import sys
import json
import argparse
import time

import boto.swf
from boto.swf.exceptions import SWFDomainAlreadyExistsError, \
    SWFTypeAlreadyExistsError


class SWF(object):
    def __init__(self, config_file):
        self.conf = json.load(open(config_file))
        self.layer = boto.swf.layer1.Layer1(
            aws_access_key_id=self.conf['aws']['aws_id'],
            aws_secret_access_key=self.conf['aws']['aws_secret'])

        # self.s3conn = boto.connect_s3(
        #         aws_access_key_id=self.conf['aws']['aws_id'],
        #         aws_secret_access_key=self.conf['aws']['aws_secret'],
        #         )

    def terminate(self):
        workflows = self.layer.list_open_workflow_executions(
            self.conf['aws']['swf']['domain'], oldest_date=1
        )

        for workflow in workflows['executionInfos']:
            workflow_id = workflow['execution']['workflowId']
            self.layer.terminate_workflow_execution(
                self.conf['aws']['swf']['domain'], workflow_id)
            print(workflow_id, file=sys.stderr)

    def register(self):
        self.register_domain()
        self.register_workflow_type()
        self.register_activity_type()

    def register_domain(self):
        domain = self.conf['aws']['swf']['domain']

        try:
            self.layer.register_domain(domain, '7')
        except SWFDomainAlreadyExistsError:
            print('domain', domain, 'exists', file=sys.stderr)

        # print layer.list_domains('REGISTERED')

    def register_workflow_type(self):
        domain = self.conf['aws']['swf']['domain']
        workflow = self.conf['aws']['swf']['workflow_type']
        version = '1.0'

        try:
            self.layer.register_workflow_type(
                domain, workflow, version,
                task_list=self.conf['aws']['swf']['decider_task_list'],
                default_child_policy='REQUEST_CANCEL',
                default_execution_start_to_close_timeout='31536000',
                default_task_start_to_close_timeout='31536000',
            )
        except SWFTypeAlreadyExistsError:
            print('workflow', workflow, 'exists', file=sys.stderr)

    def register_activity_type(self):
        domain = self.conf['aws']['swf']['domain']
        activity = self.conf['aws']['swf']['activity_type']
        version = '1.0'

        try:
            self.layer.register_activity_type(
                domain, activity, version,
                default_task_heartbeat_timeout='31536000',
                default_task_schedule_to_close_timeout='31536000',
                default_task_schedule_to_start_timeout='31536000',
                default_task_start_to_close_timeout='31536000',
                task_list=self.conf['aws']['swf']['worker_task_list'],
            )
        except SWFTypeAlreadyExistsError:
            print('activity', activity, 'exists', file=sys.stderr)


def main():
    args = read_args()
    swf = SWF(args.config_file)

    if args.register:
        swf.register()

    if args.terminate:
        print('terminating ...', file=sys.stderr)
        swf.terminate()
        time.sleep(3)
        swf.terminate()


def read_args():
    parser = argparse.ArgumentParser(description='cmd line instance control')
    parser.add_argument('-t', '--terminate', action='store_true',
                        help='terminate open workflows')
    parser.add_argument('-r', '--register', action='store_true')
    parser.add_argument('-c', '--config-file')
    parser.set_defaults(
        config_file='setup/config.dev.json'
    )

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
