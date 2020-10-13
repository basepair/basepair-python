'''
Python interface to Basepair's REST API

Copyright [2015] - [2018] Basepair INC
All Rights Reserved.

NOTICE: All information contained herein is, and remains
the property of Basepair INC and its suppliers, if any.
The intellectual and technical concepts contained
herein are proprietary to Basepair INC
and its suppliers and may be covered by U.S. and Foreign Patents,
patents in process, and are protected by trade secret or copyright law.
Dissemination of this information or reproduction of this material
is strictly forbidden unless prior written permission is obtained
from Basepair INC.
'''
from __future__ import division
from __future__ import print_function

from builtins import object
import os
import sys
import json
import subprocess
from subprocess import CalledProcessError
import time
import datetime

import requests
from requests.exceptions import ConnectionError
from tabulate import tabulate


class BpApi(object):

    """ A wrapper over the REST API for accessing the Basepair system

    Use it thus:

    > import basepair
    > bp = basepair.connect()

    conf is a JSON object with at least these keys:
    {
        "api": {
            "host": "http://app.basepairtech.com/",
            "prefix": "api/v1/",
            "username": "utk",
            "api_key": "xxx"
        },
        "aws": {
            "s3": {
               "bucket": "basepair"
            }
        }
    }

    Some of the common methods are:

    # create a sample
    sample_id = bp.create_sample(info_dict)

    #  create an analysis
    analysis_id = bp.create_analysis(workflow_id, sample_id)

    # download results - bam, dedup file
    filename = bp.get_file_by_tags(sample_id, ['bam', 'dedup'])

    # delete sample
    bp.delete_sample(sample_id)
    """

    def __init__(self, conf=None, scratch=None, use_cache=False,
                 verbose=None):
        self.verbose = verbose

        # fetch  the configuration data

        if conf:
            self.conf = conf
        elif 'BP_CONFIG_FILE' in os.environ:
            self.conf = json.load(open(os.environ['BP_CONFIG_FILE']))
        else:
            if 'BP_USERNAME' not in os.environ:
                print('ERROR: BP_USERNAME not set in env', file=sys.stderr)
                sys.exit(1)
            if 'BP_API_KEY' not in os.environ:
                print('ERROR: BP_API_KEY not set in env', file=sys.stderr)
                sys.exit(1)
            username = os.environ['BP_USERNAME']
            api_key = os.environ['BP_API_KEY']
            self.conf = {
                'api': {
                    'host': 'https://app.basepairtech.com/',
                    'prefix': 'api/v1/',
                    'username': username,
                    'api_key': api_key
                }
            }

        aws_cfg = self.conf.get('aws', {})
        if 'AWS_CONFIG_FILE' not in os.environ and 'aws' in self.conf:
            os.environ['AWS_ACCESS_KEY_ID'] = aws_cfg.get('aws_id', '')
            os.environ['AWS_SECRET_ACCESS_KEY'] = aws_cfg.get('aws_secret', '')

        if not scratch:
            scratch = '.'

        self.scratch = self.conf.get('scratch', scratch).rstrip('/')
        self.use_cache = use_cache

        if use_cache and self.verbose == 1:
            print('Warning: caching info', file=sys.stderr)

        self.payload = {
            'username': self.conf['api']['username'],
            'api_key': self.conf['api']['api_key']
        }
        self.headers = {'content-type': 'application/json'}
        self.get_userid()

        self.genomes = self.get_genomes()

        self.DATATYPES = ['dna-seq', 'chip-seq', 'rna-seq', 'atac-seq',
                          'other']
        self.LIST_TYPES = ['samples', 'analyses', 'genomes', 'workflows',
                           'analysis']

    def _check_genome(self, genome):
        """Check if the genome is in the Basepair database"""

        if not any([genome in i['name'] for i in self.genomes]):
            print(('The provided genome, {genome}, does not exist in ' +
                   'Basepair! Proceeding anyway...').format(genome=genome),
                  file=sys.stderr)

    def _check_sample(self, uid):
        """Check if the sample is in the Basepair database"""

        res = self.get_sample(uid, add_analysis=False)
        if res:
            return True
        print('The provided sample id: {id}, does not exist in Basepair!'.format(id=uid)
              , file=sys.stderr)
        return False

    def _check_workflow(self, uid):
        """Check if the workflow is in the Basepair database"""

        res = self.get_workflow(uid)
        if res:
            return True
        print('The provided workflow id: {id}, does not exist in Basepair!'.format(id=uid)
              , file=sys.stderr)
        return False

    def get_request(self, url, user_params=None, verify=True):
        """Add params to GET request"""
        params = self.payload
        if user_params:
            params.update(user_params)

        try:
            res = requests.get(url, params=params, verify=verify)
        except ConnectionError:
            print('connection error', file=sys.stderr)
            print(url, file=sys.stderr)
            return None, None

        data = res.json() if res.status_code == 200 else None

        if res.status_code != 200:
            print('code:', res.status_code, 'for', url, file=sys.stderr)

        return data, res.status_code

    def post_request(self, url, data, verify=True):
        """Add params to POST request"""
        return requests.post(url, data=json.dumps(data), params=self.payload,
                             headers=self.headers, verify=verify)

    def put_request(self, url, data, verify=True):
        """Add params to PUT request, data is pure json"""
        return requests.put(url, data=json.dumps(data), params=self.payload,
                            headers=self.headers, verify=verify)

    def patch_request(self, url, data, verify=True):
        """Add params to PATCH request"""
        return requests.patch(url, data=json.dumps(data), params=self.payload,
                              headers=self.headers, verify=verify)

    def delete_request(self, url, verify=True):
        """Add params to DELETE request"""
        return requests.delete(url, params=self.payload, verify=verify)

    def get_url(self, kind=None, uid=None):
        """Create URL for a given object kind, add id if provided"""
        # url = self.conf['api']['url'] + kind
        url = self.conf['api']['host'] + self.conf['api']['prefix'] + kind
        if uid:
            url = '{}/{}'.format(url, uid)

        return url

    def get_user_url(self, uid=None):
        """Get URL for accessing 1 sample or all samples"""
        return self.get_url('users', uid)

    def get_sample_url(self, uid=None):
        """Get URL for accessing 1 sample or all samples"""
        return self.get_url('samples', uid)

    def get_project_url(self, uid=None):
        """Get URL for accessing 1 project or all projects"""
        return self.get_url('projects', uid)

    def get_genomefile_url(self, uid=None):
        """Get URL for accessing 1 genomefile or all genomefiles"""
        return self.get_url('genomefiles', uid)

    def get_group_url(self, uid=None):
        """Get URL for accessing 1 group or all groups"""
        return self.get_url('groups', uid)

    def get_analysis_url(self, uid=None):
        """Get URL for accessing 1 analysis or all analysis"""
        return self.get_url('analyses', uid)

    def get_file_url(self, uid=None):
        """Get URL for accessing 1 file or all files"""
        return self.get_url('files', uid)

    def get_upload_url(self, uid=None):
        """Get URL for accessing 1 upload or all uploads"""
        return self.get_url('uploads', uid)

    def get_genome_url(self, uid=None):
        """Get URL for accessing 1 genome or all genomes"""
        return self.get_url('genomes', uid)

    def get_gene_url(self, uid=None):
        """Get URL for accessing 1 gene or all genes"""
        return self.get_url('genes', uid)

    def parse_url(self, url):
        """Parse URL to get the id, and other stuff"""
        parts = url.rsplit('/', 1)
        return {
            'id': parts[1]
        }

    def get_id_from_url(self, url):
        """Parse URL to get the id"""
        return self.parse_url(url)['id']

    def get_userid(self):
        """Get userid, username provided in conf"""
        url = '{}/?username={}'.format(
            self.get_url('users'), self.conf['api']['username'])
        res, code = self.get_request(url)

        self.conf['user'] = res['objects'][0]

    def get_info(self, kind, uid):
        """Get a object, save to disk and then load it as a JSON object"""

        if uid is None:
            print('Your provided uid is invalid: {}'.format(uid))
            return

        if self.use_cache:
            # construct cache filename
            filename = self.scratch + '/json/{}.{}.json'.format(kind, uid)
            filename = os.path.expanduser(filename)

            # get from server - no data in cache or empty cache
            if not os.path.exists(filename) or not os.path.getsize(filename):
                # make directory for storing files
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))

                url = self.get_url(kind, uid)
                if self.verbose == 2:
                    print('getting', url, file=sys.stderr)
                info, code = self.get_request(url)

                # save to disk
                if info:
                    with open(filename, 'w') as handle:
                        handle.write(json.dumps(info, indent=2))

            # read from cache
            else:
                info = json.loads(open(filename, 'r').read().strip())
                code = 200

        # don't use cache
        else:
            url = self.get_url(kind, uid)
            if self.verbose == 2:
                print('getting', url, file=sys.stderr)
            info, code = self.get_request(url)

        return info, code

    def get_all_info(self, kind):
        """Get all objects of a kind as JSON object"""
        url = self.get_url(kind)
        info, code = self.get_request(url)

        return info

    def get_user(self, uid):
        info, code = self.get_info(kind='users', uid=uid)
        return info

    def get_module(self, uid):
        info, code = self.get_info(kind='modules', uid=uid)
        return info

    def get_workflow(self, uid):
        info, code = self.get_info(kind='workflows', uid=uid)
        return info

    def get_workflows(self):
        info = self.get_all_info(kind='workflows')

        workflows = []
        for i in info:
            workflows.append(self.get_workflow(i['id']))

        return workflows

    def get_uploads(self):
        """Get all uploads as JSON object"""
        info = self.get_all_info(kind='uploads')
        return info

    def get_upload(self, uid):
        """Get a single upload as JSON object"""
        info, code = self.get_info(kind='uploads', uid=uid)
        return info

    def get_samples(self):
        info = self.get_all_info(kind='samples')
        return info

    def get_sample(self, uid, add_analysis=True):
        info, code = self.get_info(kind='samples', uid=uid)
        if info:
            if add_analysis:
                info = self.add_full_analysis(info)
        return info

    def create_analysis(self, workflow_id, sample_id=None, sample_ids=None,
                        control_id=None, control_ids=None, project_id=None,
                        params=None, ignore_validation_warnings=False):
        """Start analysis

        Parameters
        ----------
        workflow_id : str or int
            id number for the workflow. Run bp.get_workflows() to see what
            is available.

        sample_id : str
            Sample id number.

        sample_ids : list (optional)
            List of sample id number.

        control_id : str (optional)
            Control sample id number.

        control_ids : list (optional)
            Control sample id numbers.

        params : dict
            Dictionary of parameter values.

        ignore_validation_warnings : boolean (optional)
            Ignore validation warnings

        """

        # check if valid workflow id
        if not self._check_workflow(workflow_id):
            return

        if sample_id:
            sample_ids = [sample_id]
        if not sample_ids:
            sample_ids = []

        # check if all sample ids valid
        if not all([self._check_sample(s_id) for s_id in sample_ids]):
            return

        analysis_id = None
        url = self.get_analysis_url()
        data = {
            'controls': [],
            'ignore_validation_warning': ignore_validation_warnings,
            'samples': [],
            'workflow': '/api/v1/pipelines/{}'.format(workflow_id)
        }

        for sample_id in sample_ids:
            data['samples'].append('/api/v1/samples/{}'.format(sample_id))

        if control_id:
            control_ids = [control_id]
        if not control_ids:
            control_ids = []
        for control_id in control_ids:
            data['controls'].append('/api/v1/samples/{}'.format(control_id))

        if project_id:
            data['projects'] = ['/api/v1/projects/{}'.format(project_id)]
        print(json.dumps(data, indent=2), file=sys.stderr)

        if params:
            # data['params'] = json.dumps(params)
            data['params'] = params

        res = self.post_request(url, data)

        if res.status_code == 201:
            analysis_id = self.parse_url(res.headers['location'])['id']
            if self.verbose:
                print('created: analysis {} with sample id(s) {}'.format(
                    analysis_id, ','.join(sample_ids)), file=sys.stderr)
        else:
            error_msgs = {
                401: 'You don\'t have access to this resource.',
                404: 'Resource not found.',
                500: 'Error retrieving data from API!'
            }
            try:
                res = res.json()
                error_obj = res.get('error')
                if isinstance(error_obj, dict):
                    # handles error object with the format:
                    # {error:True, error_msgs:[], warning:True, warning_msgs:[]}
                    if error_obj.get('error'):
                        print('Errors:')
                        for msg in error_obj.get('error_msgs'):
                            print('- ', msg)
                    if error_obj.get('warning'):
                        print('Warnings (pass -i or --ignore_warning to ignore warnings):')
                        for msg in error_obj.get('warning_msgs'):
                            print('- ', msg)
                else:
                    # legacy
                    print(error_obj)
            except ValueError:
                if res.status_code in error_msgs:
                    print(error_msgs[res.status_code], file=sys.stderr)
                else:
                    print('Error occurred.')
        return analysis_id

    def add_full_analysis(self, sample):
        """Add full analysis info to the sample"""
        analysis_ids = [self.parse_url(uri)['id']
                        for uri in sample['analyses']]
        analyses = [self.get_analysis(uid)[0] for uid in analysis_ids]
        # remove null analyses, probably deleted or no ownership
        analyses = [x for x in analyses if x]

        sample['analyses_full'] = analyses
        return sample

    def get_sample_owner_id(self, sample_id):
        info = self.get_sample(sample_id)
        if info:
            return self.parse_url(info['owner'])['id']
        else:
            return None

    def get_sample_owner(self, sample_id):
        user_id = self.get_sample_owner_id(sample_id)
        if user_id:
            return self.get_user(user_id)
        else:
            return None

    def get_analyses(self):
        info = self.get_all_info(kind='analyses')
        return info

    def get_analysis(self, uid):
        info, code = self.get_info(kind='analyses', uid=uid)
        return info, code

    def get_analysis_owner_id(self, analysis_id):
        info, code = self.get_analysis(analysis_id)
        if info:
            return self.parse_url(info['owner'])['id']
        else:
            return None

    def get_analysis_owner(self, analysis_id):
        """get owner user for analysis"""

        user_id = self.get_analysis_owner_id(analysis_id)

        if user_id:
            return self.get_user(user_id)
        else:
            return None

    def get_genome(self, uid):
        info, code = self.get_info(kind='genomes', uid=uid)
        return info

    def get_genomes(self):
        info = self.get_all_info(kind='genomes')
        return info

    def create_genome(self, data):
        url = self.get_genome_url()
        res = self.post_request(url, data)
        return res

    def update_genome(self, uid, data):
        url = self.get_genome_url(uid)
        res = self.put_request(url, data)
        if self.verbose and res.status_code == 204:
            print('genome', uid, 'updated', file=sys.stderr)
        return res

    def delete_genome(self, uid):
        url = self.get_genome_url(uid)
        return self.delete_request(url)

    def get_gene(self, uid):
        info, code = self.get_info(kind='genes', uid=uid)
        return info

    def get_genes(self):
        info = self.get_all_info(kind='genes')
        return info

    def get_genes_by_info(self, genome=None, symbol=None, tx_id=None):
        params = {}
        if genome:
            params['genome__name'] = genome
        if symbol:
            params['symbol__iexact'] = symbol
        if tx_id:
            params['tx_id'] = tx_id

        # use get request with params
        url = self.get_gene_url()
        return self.get_request(url, user_params=params)

    def create_gene(self, data):
        url = self.get_gene_url()
        res = self.post_request(url, data)
        return res

    def update_gene(self, uid, data):
        url = self.get_gene_url(uid)
        res = self.put_request(url, data)
        if self.verbose and res.status_code == 204:
            print('gene', uid, 'updated', file=sys.stderr)
        return res

    def delete_gene(self, uid):
        url = self.get_gene_url(uid)
        return self.delete_request(url)

    def get_group(self, uid):
        info, code = self.get_info(kind='groups', uid=uid)
        return info

    def get_file(self, uid):
        info, code = self.get_info(kind='files', uid=uid)
        return info

    def get_host_by_domain(self, domain):
        url = self.get_url('hosts')
        url += '?domain={}'.format(domain)
        response, status = self.get_request(url)
        try:
            return response[0]
        except IndexError:
            return None

    def sample_name_to_id(self, name):
        url = self.get_sample_url()
        info, code = self.get_request(url, user_params={'name': name})

        if not len(info):
            print('warning: no sample by name', name, file=sys.stderr)
            return None
        elif len(info) == 1:
            return info[0]['id']
        else:
            print('warning: multiple sample by name', name, file=sys.stderr)
            return info[0]['id']

    def create_project(self, data):
        url = self.get_project_url()
        res = self.post_request(url, data)

        if self.verbose == 2:
            print('Posting url:', url, file=sys.stderr)
            print('Data:', data, file=sys.stderr)

        project_id = None
        # success
        if res.status_code == 201:
            project_id = self.parse_url(res.headers['location'])['id']
            if self.verbose:
                print('created: project with id', project_id,
                      file=sys.stderr)

        # failure
        else:
            print('failed project creation:', data['name'],
                  res.status_code, res.reason, file=sys.stderr)

        return project_id

    def create_sample(self, data, source='api', upload=True):
        """Create sample with the provided info

        Parameters
        ----------
        data : dict
            Dictionary of sample information.

        source : str
            TODO

        upload : bool
            Whether to upload the sample to the server or not.

        """

        # some input validation

        if data.get('genome'):
            self._check_genome(data['genome'])

        if data.get('default_workflow'):
            if not self._check_workflow(data['default_workflow']):
                del data['default_workflow']
                print('Provided workflow is not valid!', file=sys.stderr)

        if 'filepaths1' in data and data['filepaths1'] is None:

            if self.verbose:
                print('filepaths1 is None!', file=sys.stderr)

            del data['filepaths1']

        if 'filepaths2' in data and data['filepaths2'] is None:

            if self.verbose:
                print('filepaths2 is None!', file=sys.stderr)

            del data['filepaths2']

        url = self.get_sample_url()

        if data.get('default_workflow'):
            data['default_workflow'] = '/api/v1/pipelines/{}'.format(
                data['default_workflow'])

        sample_id = None
        if 'id' not in data:
            res = self.post_request(url, data)

            if self.verbose == 2:
                print('Posting url:', url, file=sys.stderr)
                print('Data:', data, file=sys.stderr)

            # success
            if res.status_code == 201:
                sample_id = self.parse_url(res.headers['location'])['id']
                if self.verbose:
                    print('created: sample with id', sample_id,
                          file=sys.stderr)

            # failure
            else:
                print('Failed sample creation:', data['name'],
                      res.status_code, res.reason, file=sys.stderr)
                try:
                    res = res.json()
                    print(res.get('error'))
                except ValueError:
                    print('Error occurred.')

        else:
            sample_id = data['id']

        # if only one sample as str, but into list

        if data.get('filepaths1'):
            if type(data['filepaths1']) == str:
                data['filepaths1'] = [data['filepaths1']]

        if data.get('filepaths2'):
            if type(data['filepaths2']) == str:
                data['filepaths2'] = [data['filepaths2']]

        # do the actual upload, update filepath

        files_to_upload = []
        for i, path in enumerate(data.get('filepaths1', [])):
            data['filepaths1'][i] = os.path.abspath(os.path.expanduser(
                os.path.expandvars(data['filepaths1'][i])))
        for i, path in enumerate(data.get('filepaths2', [])):
            data['filepaths2'][i] = os.path.abspath(os.path.expanduser(
                os.path.expandvars(data['filepaths2'][i])))

        # if a sample id exists, then upload the files

        if sample_id:

            if self.verbose:
                print('Sample id: {}'.format(sample_id), file=sys.stderr)

            # upload the first set of files

            order = 0
            for filepath in data.get('filepaths1', []):

                if self.verbose:
                    print('Creating upload {}'.format(filepath),
                          file=sys.stderr)

                upload_id, filepath, key = self.create_upload(
                    sample_id, filepath, order,
                    is_paired_end=False, source=source)
                files_to_upload.append([upload_id, filepath, key])
                order += 1

            # upload the second set of files

            for filepath in data.get('filepaths2', []):

                if self.verbose:
                    print('Creating upload {}'.format(filepath),
                          file=sys.stderr)

                upload_id, filepath, key = self.create_upload(
                    sample_id, filepath, order,
                    is_paired_end=True, source=source)
                files_to_upload.append([upload_id, filepath, key])
                order += 1

            if upload:
                for upload_id, filepath, key in files_to_upload:

                    if self.verbose:
                        print(
                            ('Uploading. upload_id: {}, ' +
                             'filepath: {}, key: {}').format(
                                 upload_id, filepath, key),
                            file=sys.stderr)

                    self.upload_file(upload_id, filepath, key)

        return sample_id

    def create_upload(self, sample_id, filepath, order, is_paired_end,
                      source='api'):
        """Create a upload object and actually upload the file"""
        filesize = None
        status = 'in_progress'
        if filepath.startswith('ftp://'):
            key = filepath
            status = 'completed'
        else:
            key = 'uploads/{}/{}/{}'.format(
                self.conf['user']['id'], sample_id, os.path.basename(filepath))
            filesize = os.stat(filepath).st_size \
                if os.path.exists(filepath) else 0

        # update record with location of uploaded file
        url = self.get_upload_url()
        data = {
            'sample': self.get_sample_url(sample_id),
            'key': key,
            'filesize': filesize,
            # 'timetaken': seconds_to_upload,
            'status': status,
            'order': order,
            'is_paired_end': is_paired_end,
            'source': source,
        }
        res = self.post_request(url, data)

        if res.status_code == 201:
            upload_id = self.parse_url(res.headers['location'])['id']
            if self.verbose:
                print('\tcreated: upload with id', upload_id, file=sys.stderr)

            return upload_id, filepath, key

        else:
            return None, None, None

    # update file to S3 and update info
    def upload_file(self, upload_id, filepath, key):
        starttime = time.time()
        self.copy_file(filepath, key, action='to')
        seconds_to_upload = int(time.time() - starttime)

        data = {
            'filesize': os.stat(filepath).st_size,
            'status': 'completed',
            'timetaken': seconds_to_upload,
            'seq_length': 0,
        }
        self.update_upload(upload_id, data)

    def create_file(self, uid, data):
        url = self.get_file_url()
        res = self.post_request(url, data)

        return res

    def fusionsalysis(self, workflow_id, sample_id=None, sample_ids=None,
                        control_id=None, control_ids=None, params=None):
        """Start analysis"""
        analysis_id = None
        url = self.get_analysis_url()
        data = {
            'workflow': '/api/v1/pipelines/{}'.format(workflow_id),
            'samples': [],
            'controls': [],
        }

        if sample_id:
            sample_ids = [sample_id]
        if not sample_ids:
            sample_ids = []
        for sample_id in sample_ids:
            data['samples'].append('/api/v1/samples/{}'.format(sample_id))

        if control_id:
            control_ids = [control_id]
        if not control_ids:
            control_ids = []
        for control_id in control_ids:
            data['controls'].append('/api/v1/samples/{}'.format(control_id))

        if params:
            # data['params'] = json.dumps(params)
            data['params'] = params

        res = self.post_request(url, data)

        if res.status_code == 201:
            analysis_id = self.parse_url(res.headers['location'])['id']
            if self.verbose:
                print('created: analysis {} w/ sample {}'.format(
                    analysis_id, ','.join(sample_ids)), file=sys.stderr)

        else:
            print('failed:', ','.join(sample_ids),
                  res.status_code, file=sys.stderr)

        return analysis_id

    def update_upload(self, uid, data):
        url = self.get_upload_url(uid)
        res = self.put_request(url, data)
        return res

    def update_sample(self, uid, data):
        url = self.get_sample_url(uid)
        res = self.put_request(url, data)
        if self.verbose and res.status_code == 204:
            print('sample', uid, 'updated', file=sys.stderr)
        return res

    def update_project(self, uid, data, params=None):
        url = self.get_project_url(uid)
        if params:
            url += '?params=' + json.dumps(params)
        res = self.put_request(url, data)
        if self.verbose and res.status_code == 204:
            print('project', uid, 'updated', file=sys.stderr)
        return res

    def update_analysis(self, uid, data):
        url = self.get_analysis_url(uid)
        res = self.put_request(url, data)
        if res.status_code == 204:
            if self.verbose:
                print('analysis', uid, 'updated', file=sys.stderr)
        else:
            print('cudnt update analysis {}, code {}'.format(
                uid, res.status_code), file=sys.stderr)
        return res

    def update_file(self, uid, data):
        url = self.get_file_url(uid)
        res = self.put_request(url, data)
        return res

    def delete_sample(self, uid):
        url = self.get_sample_url(uid)
        res = self.delete_request(url)

        if res.status_code == 204:
            if self.verbose:
                print('deleted sample', uid, file=sys.stderr)
        else:
            print('error: deleting {}, code {}, {}'.format(
                uid, res.status_code, res.reason), file=sys.stderr)
        return res

    def delete_analysis(self, uid):
        url = self.get_analysis_url(uid)
        return self.delete_request(url)

    def delete_upload(self, uid):
        url = self.get_upload_url(uid)
        return self.delete_request(url)

    def copy_file(self, src, dest, action='to'):
        if action == 'to':
            return self.copy_file_to_s3(src, dest)
        else:
            return self.copy_file_from_s3(src, dest)

    def copy_file_from_s3(self, src, dest):
        """
        Low level function to copy a file from cloud to disk

        Parameters
        ----------
        src - str
            File path on AWS S3, not including the bucket

        dest - str
            Directory or file path where file will be downloaded to

        """

        src = 's3://{}/{}'.format(self.conf['aws']['s3']['bucket'], src)
        cmd = self.get_copy_cmd(src, dest)
        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True)
            return output
        except subprocess.CalledProcessError as stderr:
            print("Error downloading {}.".format(src))
            print("Return code: {}".format(stderr.returncode))
            print("Ouput: {}".format(stderr.output))
            return False

    def copy_file_to_s3(self, src, dest, params=None):
        """Low level function to copy a file to cloud from disk"""
        dest = 's3://{}/{}'.format(self.conf['aws']['s3']['bucket'], dest)

        # check if file is current
        # if self.is_file_current(src, dest):
        #     return False

        cmd = self.get_copy_cmd(src, dest, sse=True, params=params)

        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, shell=True)
            return output
        except CalledProcessError as e:
            print('error in copy file to s3', file=sys.stderr)
            print(cmd, file=sys.stderr)
            print(e.output, file=sys.stderr)
            return None
        else:
            if self.verbose:
                print('copying', src, 'to', dest, file=sys.stderr)

    def get_copy_cmd(self, src, dest, sse=False, params=None):
        """
        Create copy cmd based on AWS cli utility

        Parameters
        ----------
        src - str
            Path to file on AWS S3

        dest - str
            Destination directory or path where file will be downloaded to

        sse - bool
            Whether to use sever side encryption

        params - dict
            Other download paramters

        """
        _params = ''
        if sse:
            _params = '--sse'
        if params:
            for arg, val in params.items():
                _params += ' {} "{}"'.format(arg, val)

        cmd = ('aws s3 cp "{}" "{}" {}').format(
                  src, dest, _params)

        return cmd

    def is_file_current(self, filepath, key_name):
        cmd = 'aws s3 ls {}'.format(key_name)

        statinfo = os.stat(filepath)
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        key = self.bucket.get_key(key_name)

        if key and statinfo.st_size == key.size:
            return True
        else:
            return False

    def get_history(self, analysis_id, outdir=None):
        """
        Get SWF history for the analysis

        Parameters
        ----------
        analysis_id - int
            Analysis ID

        outdir - str
            (Optional) Directory to save data. Use instead of scratch.
        """
        user_id = self.get_analysis_owner_id(analysis_id)
        filekey = 'log/analyses/{}/{}/history.json'.format(
            user_id, analysis_id)

        if outdir:
            filename = '{}/history/history.{}.json'.format(
                outdir, analysis_id)
        else:
            filename = '{}/history/history.{}.json'.format(
                self.scratch, analysis_id)

        return self.download_file(filekey, filename, load=True, is_json=True)

    def get_log(self, analysis_id, outdir=None):
        """
        Get log file for the analysis

        Parameters
        ----------
        analysis_id - int
            Analysis ID

        outdir - str
            (Optional) Directory to save data. Use instead of scratch.
        """
        user_id = self.get_analysis_owner_id(analysis_id)
        filekey = 'log/analyses/{}/{}/worker.log'.format(
            user_id, analysis_id)

        if outdir:
            filename = '{}/worker.{}.log'.format(
                outdir, analysis_id)
        else:
            filename = '{}/worker.{}.log'.format(
                self.scratch, analysis_id)

        return self.download_file(filekey, filename, load=False, is_json=False)

    def get_filepath(self, filename, dirname=None):
        """Use scratch and [dirname] to construct a full filepath"""

        # move along, nothin to do
        if filename.startswith('/'):
            filepath = filename

        else:
            if dirname:
                filename = '{}/{}'.format(dirname.rstrip('/'), filename)

            # adding dirname made it full
            if filename.startswith('/'):
                filepath = filename
            else:
                filepath = self.scratch + '/' + filename

        return filepath

    def download_raw_files(self, sample, outdir=None):
        """
        Download raw data associated with a sample

        Parameters
        ----------
        sample - sample object
            From calling bp.get_sample()

        outdir - str
            Output directory to save files to!

        """

        uploads = sample['uploads']
        files = [upload['key'] for upload in uploads]
        files_downloaded = []

        for file_i in files:
            if outdir:

                # check if present

                fileout = os.path.join(outdir, os.path.split(file_i)[1])

                if os.path.exists(fileout):
                    print('Not downloading. File exists: {}'.format(fileout))
                    output = True
                else:
                    output = self.copy_file_from_s3(file_i, outdir)

                if output:
                    print('Downloaded {} to {}!'.format(
                        os.path.split(file_i)[1], outdir))
                    files_downloaded.append(fileout)
            else:

                # check if present

                fileout = os.path.join(self.scratch, os.path.split(file_i)[1])

                if os.path.exists(fileout):
                    print('Not downloading. File exists: {}'.format(fileout))
                    output = True
                else:
                    output = self.copy_file_from_s3(file_i, self.scratch)

                if output:
                    print('Downloaded {} to {}!'.format(
                        os.path.split(file_i)[1], self.scratch))
                    files_downloaded.append(fileout)

        return files_downloaded

    def download_file(self, filekey, filename=None, dirname=None, load=False,
                      is_json=False):
        """
        High level function, downloads to scratch dir and opens and
        parses files to JSON if asked. Uses low level copy_file()

        Parameters
        ----------

        filekey - str
            (Required) The full file path on AWS S3.

        filename - str
            (Optional) Give the download file a new name.

        dirname - str
            (Optional) Directory to download the file to.

        load - bool
            (Optional) Load the file after downloading.

        isjson - bool
            (Optional) Whether the downloaded file is JSON format.

        Returns
        -------

        Absolute filepath to downloaded file.

        """

        if not filename:

            # don't renaming the file
            # get the download directory
            if dirname:
                if dirname.startswith('/'):
                    prefix = dirname
                else:
                    prefix = os.path.join(self.scratch, dirname)
            else:
                prefix = self.scratch

            filepath = os.path.join(prefix, os.path.basename(filekey))
        else:

            # rename the download file
            filepath = self.get_filepath(filename, dirname=dirname)

        filepath = os.path.expanduser(filepath)

        # if file not already there, download it
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            if self.verbose:
                print('downloading', filepath, file=sys.stderr)

            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))

            self.copy_file(filekey, filepath, action='from')
        else:
            if self.verbose:
                print('exists', filepath, file=sys.stderr)

        if load:
            data = open(filepath, 'r').read().strip()
            if is_json:
                data = json.loads(data)
            return data
        else:
            return filepath

    # take a list of files and filter out those that dont have tags
    # if multiple True, return list
    def filter_files_by_tags(self, files, tags, kind='exact', exclude=None,
                             multiple=False):
        """
        Filter files that have all the tags. If exclude tags provided,
        only return the files that don't have the exclude tags.append

        In some cases, multiple files are expected, set it to true.

        Parameters
        ---------

        files - dict
            List dictionaries containing file information.

        tags - list or None
            List of tags.

        kind - str
            Type of tag filtering. Options: exact, subset

        exclude - list
            List of tags to exclude.

        multiple - bool
            Whether to return all matching files or only one.

        Returns
        -------
        A list of files
        """

        if tags is None:
            return files

        if type(tags) != list:
            print('Invalid tags argument! Provide a list of tags.')
            return

        # filter for matches

        if not kind or kind == 'exact':
            files = [x for x in files
                     if x['tags'] and set(tags) == set(x['tags'])]
        elif kind == 'subset':
            files = [x for x in files
                     if x['tags'] and set(tags).intersection(set(x['tags']))]

        # exclude files by tag

        if exclude:
            files = [x for x in files if x['tags'] and not set(
                x['tags']).intersection(set(exclude))]

        if kind == 'diff':
            files = [x for x in files if x['tags'] and not set(
                x['tags']).intersection(set(tags))]

        # check if no files left after filtering

        if len(files) == 0:
            print('No matching files after filtering by tags:',
                  tags,
                  file=sys.stderr)
            return None

        # return files

        if multiple:
            return files
        else:
            if len(files) == 1:
                return files
            elif len(files) > 1:
                print('multiple matches for tags:', tags, file=sys.stderr)
                return files[0:1]

    def get_analysis_files(self, analysis, tags=None, kind='exact',
                           dest=None, dirname=None):
        """
        For a analysis, go through files and get that match the tags

        Parameters
        ----------

        analysis - dict
            The dictionary returned by bp.get_analysis().

        tags - list[list,list,...] or None
            List of lists of tags to filter by.

        kind - str
            Type of tag filtering. Options: exact, subset

        dirname - str
            Directory to download files to.

        """

        # some input checking

        if tags is not None:
            if type(tags) != list:
                print(
                    'Invald tags argument. Provide a list of list of tags.',
                    file=sys.stderr)
                return
            else:
                if any([type(i) != list for i in tags]):
                    print(
                        'Invald tags argument. Provide a list of list of tags.',
                        file=sys.stderr)
                    return
        else:
            tags = [None]

        # filter the files

        matching_files = []
        for tags_sub in tags:
            matching_files += self.filter_files_by_tags(
                analysis['files'], tags_sub, kind=kind, multiple=True)

        if matching_files is None:
            return None

        filepaths = []

        for matching_file in matching_files:
            filepaths += self.download_file(
                matching_file['path'], dirname=dirname)

        return filepaths

    def get_file_by_tags(self, sample, tags=None, kind=None, exclude=None,
                         analysis_tags=None, workflow_id=None, dirname=None,
                         multiple=False, dest=None, download=True):
        """
        For a sample, go through analysis and get files that match the tags.

        Parameters
        ----------

        sample - str
            Dictionary of sample information.

        tags - list[list,list,...] or list
            List of list of tags for file filtering. If just list of tags,
            will convert to list of lists.

        kind - str
            Type of tag filtering to do. Options: exact, diff, or subset

        exclude - list
            List of tags to exclude.

        analysis_tags - list
            Analysis tags to filter analyses when looking for files.

        workflow_id - int
            Workflow id to look for files in.
            NOT IMPLEMENTED YET

        dirname - str
            Ouput directory to save the file to.

        multiple - bool
            Whether to return multiple files or just the first one.

        dest - str
            (Optional) File name to save the file to.

        download - bool
            Whether to download the file(s)

        """

        # some error checking

        if tags is None:
            print("Tags is None")
            return

        # make sure tags is a list of lists

        if type(tags) is list:
            if type(tags[0]) is not list:
                tags = [tags]

        # if not dirname:
        #     dirname = ''

        matches = []
        matching_file = []
        for analysis in sample['analyses_full']:
            if analysis['status'] == 'error':
                print('analysis ended in error, skipping!')
                continue

            # dont even look if not the right type of analysis
            if analysis_tags:
                if not analysis['tags']:
                    continue
                if not set(analysis_tags) <= set(analysis['tags']):
                    continue

            if analysis['params'] and 'info' in analysis['params']:
                if analysis['params']['info'].get('genome', None) is None:
                    print('Could not find genome for analysis {}'.format(
                        analysis['id']
                    ), file=sys.stderr)
                    continue
                if sample.get('genome', None) is None:
                    print('Could not find genome for analysis {}'.format(
                        analysis['id']
                    ), file=sys.stderr)
                    continue
                if analysis['params']['info']['genome'] != sample['genome']:
                    print('analysis genome {}'.format(
                        analysis['params']['info']['genome']),
                          'different from sample genome {}!'.format(
                              sample['genome']),
                          file=sys.stderr)
                    continue

            if self.verbose:
                print('looking at', analysis['id'], 'status',
                    analysis['status'], file=sys.stderr)
            for tags_sub in tags:
                filtered_files = self.filter_files_by_tags(
                    analysis['files'], tags_sub, kind=kind, exclude=exclude,
                    multiple=multiple)

                if filtered_files is not None:
                    matching_file += filtered_files

            if matching_file:
                if multiple:
                    for f in matching_file:
                        matches.append([analysis['id'], f])
                else:
                    matches.append([analysis['id'], matching_file[0]])

        if len(matches) == 0:
            print('warning: no matching file for', tags, file=sys.stderr)
            return None

        if len(matches) > 1:
            matches.sort(key=lambda x: datetime.datetime.strptime(
                x[1]['last_updated'], '%Y-%m-%dT%H:%M:%S.%f'), reverse=True)
            if not multiple:
                print('warning: multiple matching file for', tags,
                      file=sys.stderr)
            for f in matches:
                print('\t', f[1]['last_updated'], f[1]['path'],
                      file=sys.stderr)

        if multiple:
            filepath = []
            for match in matches:
                file1 = match[1]

                if download:
                    path = self.download_file(file1['path'], dirname=dirname)
                    filepath.append(path)
                else:
                    filepath.append(file1['path'])
        else:
            file1 = matches[0][1]
            # if dest:
            #     dirname = dest
            #     filepath = self.download_file(file1['path'], dest)
            # else:
            if download:
                filepath = self.download_file(
                    file1['path'], filename=dest, dirname=dirname)
            else:
                filepath = file1['path']
                print('else')

        return filepath

    # take a list of files and filter out those that dont have node
    # if multiple True, return list
    def filter_files_by_node(self, files, node, multiple=False):
        """Filter files that are from the node.

        In some cases, multiple files are expected, set it to true.
        """
        files = [fl for fl in files if fl['node'] == node]
        # filter(lambda x: x['node'] == node, files)

        if multiple:
            return files
        else:
            if len(files) == 1:
                return files[0]
            elif len(files) == 0:
                return None
            elif len(files) > 1:
                print('multiple matches for node:', node, file=sys.stderr)
                return files[0]

    # select analyses where one of the files match the tags
    # then get the first matching file
    def get_file_by_node(self, sample, node=None, analysis_tags=None,
                         dirname=None, multiple=False, dest=None):
        """For a sample, go through analysis and
        get files that match the tags
        """

        # if not dirname:
        #     dirname = ''

        matches = []
        for analysis in sample['analyses_full']:
            if analysis['status'] == 'error':
                continue

            if analysis_tags:
                if not analysis['tags']:
                    continue
                if not set(analysis_tags) <= set(analysis['tags']):
                    continue

            matching_file = self.filter_files_by_node(
                analysis['files'], node, multiple=multiple)

            if matching_file:
                if multiple:
                    for _ in matching_file:
                        matches.append([analysis['id'], _])
                else:
                    matches.append([analysis['id'], matching_file])

        if len(matches) == 0:
            print('warning: no matching file for', node, file=sys.stderr)
            return None

        if len(matches) > 1:
            matches.sort(key=lambda x: datetime.datetime.strptime(
                x[1]['last_updated'], '%Y-%m-%dT%H:%M:%S.%f'), reverse=True)
            if not multiple:
                print('warning: multiple matching file for', node,
                      file=sys.stderr)
            for _ in matches:
                print('\t', _[1]['last_updated'], _[1]['path'],
                      file=sys.stderr)

        if multiple:
            filepath = []
            for match in matches:
                file1 = match[1]
                path = self.download_file(file1['path'], dirname=dirname)
                filepath.append(path)
        else:
            file1 = matches[0][1]
            if dest:
                dirname = dest
                # filepath = self.download_file(file1['path'], dest)
            # else:
            filepath = self.download_file(
                file1['path'], filename=dest, dirname=dirname)

        return filepath

    def get_genomefile_by_filters(self, filters=None):
        if not filters:
            print('Filters required.', file=sys.stderr)
            return
        res, code = self.get_request(url=self.get_genomefile_url(), user_params=filters)
        return res

    def get_window_score_filename(self, sample, kind=None, flanking=None):
        suffix = 'score-{}-{}Kb'.format(kind, flanking / 1e3)
        suffix = suffix.replace('.0Kb', 'Kb')

        filename = '{}/score/{}.{}.dedup.{}.txt'.format(
            self.scratch, sample['slug'], sample['genome'], suffix)
        return filename

    def get_expression_count_file(self, sample, features='transcripts',
                                  multiple=False):
        """Get expression count text file - for RNA-Seq"""
        if features == 'genes':
            tags = ['expression_count', 'by_gene', 'text']
        else:
            tags = ['expression_count', 'by_transcript', 'text']
        if self.verbose:
            print('getting file w tags', tags, file=sys.stderr)
        return self.get_file_by_tags(
            sample, tags, kind='exact', analysis_tags=['alignment'],
            multiple=multiple
        )

    def get_bigwig_file(self, sample, multiple=False):
        """Get bigwig file - for ChIP-Seq"""
        tags = ['bigwig']
        return self.get_file_by_tags(
            sample, tags, kind='exact', analysis_tags=['alignment'],
            multiple=multiple
        )

    def get_bam_file(self, sample, tags=None, multiple=False):
        """Get bam file. If you want deduped bam file, call with
        tags = ['bam', 'dedup']
        """
        if not tags:
            tags = ['bam']
        return self.get_file_by_tags(
            sample, tags, analysis_tags=['alignment'], multiple=multiple
        )

    def download_analysis(self, uid, tags=None, tagkind=None, outdir='.'):
        """
        Download files from one or more analysis.

        Parameters
        ----------

        uid - int or list of ints
            One or more uids identifying the analysesself.

        tags - list[list,list,...] or None
            List of list of tags to filter files by

        tagkind - str
            Type of tag filtering to do. Options: exact, diff, subset

        outdir - str
            Output directory to download results to

        """

        if tagkind not in ['exact', 'diff', 'subset']:
            print(
                'Invalid tagkind, choose one of: exact, diff, subset',
                file=sys.stderr
            )
            return

        if tags:
            if type(tags) != list:
                print(
                    'Invald tags argument. Provide a list of list of tags.',
                    file=sys.stderr
                )
                return
            else:
                if type(tags[0]) != list:
                    print(
                        'Invald tags argument. Provide a list of list of tags.',
                        file=sys.stderr
                    )
                    return

        if type(uid) is not list:
            uid = [uid]

        for analysis_id in uid:
            analysis = self.get_analysis(analysis_id)[0]
            self.get_analysis_files(
                analysis=analysis,
                tags=tags,
                kind=tagkind,
                dirname=outdir
            )

    def print_data(self, data_type='', uid=None, json=False):
        """
        Print data associated with genomes, samples, etc..

        Parameters
        ----------

        datatype - str
            Type of data to print (e.g. workflows)

        uid - list
            One or more ids of the objects you want.

        json - bool
            By default, data is printed in a human-readable format. With json
            set to True, it prints out all data in JSON format.

        """

        if type(uid) != list:
            uid = [uid]

        # get the appropriate data
        if data_type == 'analysis':
            # get detailed info about one or more analysis
            if uid is None:
                print('Your uid is invalid: {}'.format(uid))
                return

            data = []
            for uid_i in uid:
                data_tmp = self.get_analysis(uid_i)

                if data_tmp and data_tmp[1] == 200:
                    data.append(data_tmp[0])
                else:
                    print('Analysis with uid {} invalid!'.format(uid_i))
        elif data_type == 'analyses':
            res = self.get_analyses()
            data = res.get('objects')
        elif data_type == 'genome':
            if uid is None:
                print('Your uid is invalid: {}'.format(uid))
                return

            data = []
            for uid_i in uid:
                data_tmp = self.get_genome(uid_i)

                if data_tmp:
                    data.append(data_tmp)
                else:
                    print('Genome with uid {} invalid!'.format(uid_i))
        elif data_type == 'genomes':
            data = self.get_genomes()
        elif data_type == 'sample':
            # get detailed info about one or more sample
            if uid is None:
                print('Your uid is invalid: {}'.format(uid))
                return

            data = []
            for uid_i in uid:
                data_tmp = self.get_sample(uid_i)

                if data_tmp:
                    data.append(data_tmp)
                else:
                    print('Sample with uid {} invalid!'.format(uid_i))
        elif data_type == 'samples':
            res = self.get_samples()
            data = res.get('objects')
        elif data_type == 'workflows':
            res = self.get_all_info(kind='workflows')
            data = res.get('objects')

        if data is None or len(data) == 0:
            print('Nothing found for the parameters you gave!')
            return

        # print the data in either whole or pretty format
        if json:
            for item in data:
                print(item)
                print()
            return
        else:
            if data_type == 'analysis':

                for data_i in data:
                    tmp = [
                        ['id', data_i.get('id')],
                        ['name', data_i.get('name')],
                        ['date_created', data_i.get('date_created')],
                        ['completed_on', data_i.get('completed_on')]
                    ]

                    for sample_i in data_i.get('samples', []):
                        tmp.append(['sample', sample_i.split('/')[-1]])

                    for sample_i in data_i.get('controls', []):
                        tmp.append(['control', sample_i.get('id')])

                    print()
                    print('Analysis info:')
                    print(tabulate(tmp, headers=['Variable', 'Value']))

                    print()
                    print('Analysis files:')

                    # convert only filesizes that are not None
                    for index, file_data in enumerate(data_i.get('files', [])):
                        if file_data.get('filesize', None):
                            data_i['files'][index]['filesize'] /= (1024.**3)
                        else:
                            data_i['files'][index]['filesize'] = 'NA'

                    tmp = [[
                        file.get('id'),
                        file.get('filesize'),
                        file.get('source'),
                        os.path.split(file.get('path'))[1],
                        file.get('tags')] for file in data_i.get('files', [])]
                    print(
                        tabulate(
                            tmp,
                            floatfmt='.4f',
                            headers=[
                                'id',
                                'filesize (Gigabytes)',
                                'source',
                                'name',
                                'tags'
                            ],
                            numalign='right',
                        )
                    )

                    print()
                    print()
            elif data_type == 'analyses':
                data = [[
                    analysis.get('id'),
                    analysis.get('name'),
                    analysis.get('started_on'),
                    analysis.get('completed_on'),
                    analysis.get('status'),
                    analysis.get('meta', {}).get('num_files'),
                    analysis.get('tags')] for analysis in data
                ]
                print(
                    tabulate(
                        data,
                        headers=[
                            'id',
                            'name',
                            'started on',
                            'completed on',
                            'status',
                            'num files',
                            'tags'
                        ]
                    )
                )
            elif data_type == 'genome':
                data = [[
                    genome.get('id'),
                    genome.get('name'),
                    genome.get('created_on')] for genome in data]

                print(tabulate(data, headers=['id', 'name', 'created_on']))
            elif data_type == 'genomes':
                data = [[
                    genome.get('id'),
                    genome.get('name'),
                    genome.get('created_on')] for genome in data]

                print(tabulate(data, headers=['id', 'name', 'created_on']))
            elif data_type == 'sample':
                for data_i in data:
                    print('Sample id: {}'.format(data_i.get('id')))
                    print('Sample name: {}'.format(data_i.get('name')))
                    print('Sample datatype: {}'.format(data_i.get('datatype')))
                    print('Sample genome: {}'.format(data_i.get('genome_name') or data_i.get('genome'))) # compatible with or without custom genome changes
                    print('Sample data created: {}'.format(data_i.get('date_created')))
                    print('Sample num reads: {}'.format(data_i.get('meta', {}).get('num_reads')))
                    print('Analyses:')

                    data_i = [[
                        analysis.get('id'),
                        analysis.get('name'),
                        analysis.get('started_on'),
                        analysis.get('completed_on'),
                        analysis.get('status'),
                        analysis.get('meta', {}).get('num_files'),
                        analysis.get('tags')] for analysis in data_i['analyses_full']]
                    print(
                        tabulate(
                            data_i,
                            headers=[
                                'id',
                                'name',
                                'started on',
                                'completed on',
                                'status',
                                'num files',
                                'tags'
                            ]
                        )
                    )
                    print()
                    print()
            elif data_type == 'samples':
                data = [[
                    sample.get('id'),
                    sample.get('name'),
                    sample.get('datatype'),
                    (sample.get('genome_name') or sample.get('genome')), # compatible with or without custom genome changes
                    sample.get('date_created'),
                    sample.get('meta', {}).get('num_reads')] for sample in data]
                print(
                    tabulate(
                        data,
                        headers=[
                            'id',
                            'name',
                            'datatype',
                            'genome',
                            'date created',
                            'num reads'
                        ]
                    )
                )
            elif data_type == 'workflows':
                data = [[
                    workflow.get('id'),
                    workflow.get('name'),
                    workflow.get('datatype'),
                    workflow.get('description'),
                    workflow.get('tags')] for workflow in data[:5]]
                print(
                    tabulate(
                        data,
                        headers=[
                            'id',
                            'name',
                            'datatype',
                            'description',
                            'tags'
                        ]
                    )
                )
