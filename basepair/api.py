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

# pylint: disable=too-many-lines

from __future__ import division
from __future__ import print_function

import os
import sys
import json
import subprocess
from subprocess import CalledProcessError
import time
import datetime

# App imports
from .helpers import eprint, NicePrint, SetFilter
from .infra.configuration import Parser
from .infra.webapp import Analysis, File, Gene, Genome, GenomeFile, Host, Module, Pipeline, Project, Sample, Upload, User

class BpApi(): # pylint: disable=too-many-instance-attributes,too-many-public-methods
  ''' A wrapper over the REST API for accessing the Basepair system

  Use it thus:

  > import basepair
  > bp = basepair.connect()

  conf is a JSON object with at least these keys:
  {
      "api": {
          "host": "app.basepairtech.com",
          "prefix": "/api/v2/",
          "username": "utk",
          "key": "xxx"
      },
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
  '''

  def __init__(self, conf=None, scratch='.', use_cache=False, user_cache_for_host_conf=False, verbose=None): # pylint: disable=too-many-arguments
    self.verbose = verbose

    if conf:
      self.conf = conf
    elif 'BP_CONFIG_FILE' in os.environ:
      self.conf = json.load(open(os.environ['BP_CONFIG_FILE']))
    else:
      if 'BP_USERNAME' not in os.environ:
        eprint('ERROR: BP_USERNAME not set in env')
        sys.exit(1)
      if 'BP_API_KEY' not in os.environ:
        eprint('ERROR: BP_API_KEY not set in env')
        sys.exit(1)
      username = os.environ['BP_USERNAME']
      api_key = os.environ['BP_API_KEY']
      self.conf = {
        'api': {
          'key': api_key,
          'host': 'app.basepairtech.com',
          'prefix': '/api/v2/',
          'ssl': True,
          'username': username,
        }
      }

    if self.conf.get('api', {}).get('ssl') is None:
      eprint('ERROR: The config file need to be updated. Please visit:')
      eprint('https://test.basepairtech.com/api/v2/users/api_key')
      eprint('To get your new config file.')
      sys.exit(1)

    self.scratch = self.conf.get('scratch', scratch).rstrip('/')
    self.use_cache = use_cache

    if use_cache and self.verbose == 1:
      eprint('Warning: caching data.')

    self._get_user_id()

    self.genomes = self.get_genomes()

    # Get configuration from host only if it is not set in the incoming config
    cache = False
    configuration = self.conf
    if user_cache_for_host_conf:
      eprint('INFO: Use cached host cloud service configuration.')
      cache = '{}/json/config.json'.format(self.scratch)

    if self.conf.get('api', {}).get('cli'):
      configuration = (User(self.conf.get('api'))).get_configuration(cache=cache)
    self.configuration = Parser(configuration)

  ################################################################################################
  ### ANALYSIS ###################################################################################
  ################################################################################################
  def create_analysis(
    self,
    workflow_id,
    control_id=None,
    control_ids=[],
    ignore_validation_warnings=False,
    params=None,
    project_id=None,
    sample_id=None,
    sample_ids=[],
  ): # pylint: disable=dangerous-default-value,too-many-arguments
    '''Create analysis
    Parameters
    ----------
    workflow_id:                {str}   Workflow id. Run bp.get_workflows() to see what is available.  [Required]

    control_id:                 {str}   Control sample id.
    control_ids:                {list}  Control sample id.
    ignore_validation_warnings: {bool}  Ignore validation warnings
    params:                     {dict}  Dictionary of parameter values.
    project_id:                 {str}   Project id.
    sample_id:                  {str}   Sample id.
    sample_ids:                 {list}  List of sample id.
    '''

    # get api version
    prefix = self.conf.get('api', {}).get('prefix', '/api/v2/')
    if control_id:
      control_ids.append(control_id)
    if sample_id:
      sample_ids.append(sample_id)

    # check if valid workflow id
    if not self._check_workflow(workflow_id):
      return None

    # check if all sample ids are valid
    if not all((self._check_sample(item_id) for item_id in sample_ids)):
      return None

    data = {
      'controls': self._parsed_sample_list(control_ids, prefix),
      'samples': self._parsed_sample_list(sample_ids, prefix),
      'ignore_validation_warning': ignore_validation_warnings,
      'meta': {'source': 'cli'},
      'workflow': '{}pipelines/{}'.format(prefix, workflow_id)
    }

    if project_id:
      data['projects'] = ['{}projects/{}'.format(prefix, project_id)]

    if self.verbose:
      eprint(json.dumps(data, indent=2))

    if params:
      data['params'] = params

    analysis_api = Analysis(self.conf.get('api'))
    info = analysis_api.save(payload=data)
    analysis_id = info.get('id')
    if self.verbose and analysis_id:
      eprint('created: analysis {} with sample id(s) {}'.format(
          analysis_id,
          ','.join(sample_ids),
      ))
    return analysis_id

  def restart_analysis(self, uid):
    '''Restart analysis'''
    payload = {
      'id': uid,
      'source': 'cli'
    }
    return (Analysis(self.conf.get('api'))).reanalyze(payload=payload)

  def delete_analysis(self, uid):
    '''Delete method'''
    return (Analysis(self.conf.get('api'))).delete(uid)

  def download_analysis(self, uid, outdir='.', tagkind=None, tags=None):
    '''
    Download files from one or more analysis.
    Parameters
    ----------
    uid:     {int}  One or more uids identifying the analysesself             [Required]
    outdir:  {str}  Output directory to download results to
    tagkind: {str}  Type of tag filtering to do. Options: exact, diff, subset
    tags:    {list} List of list of tags to filter files by
    '''
    if tags:
      is_not_valid = not (isinstance(tags, list) and isinstance(tags[0], list))
      if is_not_valid:
        eprint('Invalid tags argument. Provide a list of list of tags.')
        return None
    if not isinstance(uid, list):
      uid = [uid]
    for item_id in uid:
      analysis = self.get_analysis(item_id)
      self.get_analysis_files(
        analysis=analysis,
        dirname=outdir,
        kind=tagkind,
        tags=tags,
      )
    return None

  def fusionsalysis(
    self,
    workflow_id,
    control_id=None,
    control_ids=[],
    params=None,
    sample_id=None,
    sample_ids=[]
  ): # pylint: disable=dangerous-default-value,too-many-arguments
    '''Create analysis
    Parameters
    ----------
    Parameters
    ----------
    workflow_id:                {str}   Workflow id. Run bp.get_workflows() to see what is available.  [Required]

    control_id:                 {str}   Control sample id.
    control_ids:                {list}  Control sample id.
    params:                     {dict}  Dictionary of parameter values.
    sample_id:                  {str}   Sample id.
    sample_ids:                 {list}  List of sample id.
    '''

    prefix = self.conf.get('api', {}).get('prefix', '/api/v2/')
    if control_id:
      control_ids.append(control_id)
    if sample_id:
      sample_ids.append(sample_id)

    data = {
      'controls': self._parsed_sample_list(control_ids, prefix),
      'samples': self._parsed_sample_list(sample_ids, prefix),
      'workflow': '{}pipelines/{}'.format(prefix, workflow_id),
    }

    if params:
      data['params'] = params

    info = (Analysis(self.conf.get('api'))).save(payload=data)
    if info.get('error'):
      eprint('failed:', ','.join(sample_ids), info.get('msg'))
      return None

    analysis_id = info.get('id')
    if self.verbose and analysis_id:
      eprint('created: analysis {} w/ sample {}'.format(analysis_id, ','.join(sample_ids)))
    return analysis_id

  def get_analysis(self, uid):
    '''Get resource'''
    return (Analysis(self.conf.get('api'))).get(
        uid,
        cache='{}/json/analysis.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )

  def get_analysis_owner(self, analysis_id):
    '''get owner user for analysis'''
    user_id = self._get_analysis_owner_id(analysis_id)
    return self.get_user(user_id) if user_id else None

  def get_analyses(self, filters={}): # pylint: disable=dangerous-default-value
    '''Get resource list'''
    return (Analysis(self.conf.get('api'))).list_all(filters=filters)

  def update_analysis(self, uid, data):
    '''Update resource'''
    info = (Analysis(self.conf.get('api'))).save(
        obj_id=uid,
        payload=data,
    )
    if info.get('error'):
      eprint('couldn\'t update analysis {}, msg: {}'.format(uid, info.get('msg')))
      return None

    if self.verbose:
      eprint('analysis', uid, 'updated')
    return info

  ################################################################################################
  ### FILE #######################################################################################
  ################################################################################################
  def create_file(self, uid, data):
    '''Create resource'''
    return (File(self.conf.get('api'))).save(obj_id=uid, payload=data)

  def get_file(self, uid):
    '''Get resource'''
    return (File(self.conf.get('api'))).get(
        uid,
        cache='{}/json/file.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )

  def update_file(self, uid, data):
    '''Update resource'''
    return (File(self.conf.get('api'))).save(obj_id=uid, payload=data)

  ################################################################################################
  ### GENE #######################################################################################
  ################################################################################################
  def create_gene(self, data):
    '''Create resource'''
    return (Gene(self.conf.get('api'))).save(payload=data)

  def delete_gene(self, uid):
    '''Delete method'''
    return (Gene(self.conf.get('api'))).delete(uid)

  def get_gene(self, uid):
    '''Get resource'''
    return (Gene(self.conf.get('api'))).get(
        uid,
        cache='{}/json/gene.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )

  def get_genes(self):
    '''Get resource list'''
    info = (Gene(self.conf.get('api'))).list(
        params={'limit': 0}
    )
    return info.get('objects', [])

  def get_genes_by_info(self, genome=None, symbol=None, tx_id=None):
    '''Get genes by info'''
    params = {'limit': 0}
    if genome:
      params['genome__name'] = genome
    if symbol:
      params['symbol__iexact'] = symbol
    if tx_id:
      params['tx_id'] = tx_id
    info = (Gene(self.conf.get('api'))).list(params)
    return info.get('objects', [])

  def update_gene(self, uid, data):
    '''Update resource'''
    info = (Gene(self.conf.get('api'))).save(obj_id=uid, payload=data)
    if self.verbose and not info.get('error'):
      eprint('gene', uid, 'updated')
    return info

  ################################################################################################
  ### GENOME #####################################################################################
  ################################################################################################
  def create_genome(self, data):
    '''Create resource'''
    return (Genome(self.conf.get('api'))).save(payload=data)

  def delete_genome(self, uid):
    '''Delete method'''
    return (Genome(self.conf.get('api'))).delete(uid)

  def get_genome(self, uid):
    '''Get resource'''
    return (Genome(self.conf.get('api'))).get(
        uid,
        cache='{}/json/genome.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )

  def get_genomes(self, filters={}): # pylint: disable=dangerous-default-value
    '''Get resource list'''
    return (Genome(self.conf.get('api'))).list_all(filters=filters)

  def update_genome(self, uid, data):
    '''Update resource'''
    info = (Genome(self.conf.get('api'))).save(obj_id=uid, payload=data)
    if self.verbose and not info.get('error'):
      eprint('genome', uid, 'updated')
    return info

  ################################################################################################
  ### GENOME FILE ################################################################################
  ################################################################################################
  def get_genomefile_by_filters(self, filters=None):
    '''Get genome files by filters'''
    if not filters:
      eprint('Filters required.')
      return None
    filters['limit'] = 0
    info = (GenomeFile(self.conf.get('api'))).list(params=filters)
    return info.get('objects', [])

  ################################################################################################
  ### HOST #######################################################################################
  ################################################################################################
  def get_host_by_domain(self, domain):
    '''Get host by domain'''
    info = (Host(self.conf.get('api'))).list({
        'domain__exact': domain,
        'limit': 1,
    })
    return info.get('objects')[0] if info.get('objects') else None

  ################################################################################################
  ### MODULE #####################################################################################
  ################################################################################################
  def get_module(self, uid):
    '''Get resource'''
    return (Module(self.conf.get('api'))).get(
        uid,
        cache='{}/json/module.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )

  ################################################################################################
  ### PIPELINE / WORKFLOW ########################################################################
  ################################################################################################
  def get_workflow(self, uid):
    '''Get resource'''
    return (Pipeline(self.conf.get('api'))).get(
        uid,
        cache='{}/json/workflow.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )

  def get_workflows(self, filters={}): # pylint: disable=dangerous-default-value
    '''Get resource list'''
    return (Pipeline(self.conf.get('api'))).list_all(filters=filters)

  ################################################################################################
  ### PROJECT ####################################################################################
  ################################################################################################
  def create_project(self, data):
    '''Create resource'''
    info = (Project(self.conf.get('api'))).save(payload=data)
    if self.verbose == 2:
      eprint('Creating project:')
      eprint('Data:', data)

    project_id = info.get('id', None)
    if project_id:  # success
      if self.verbose:
        eprint('created: project with id', project_id)
    else:  # failure
      eprint('failed project creation:', data['name'], info.get('msg'))
    return project_id

  def update_project(self, uid, data, params=None):
    '''Update resource'''
    info = (Project(self.conf.get('api'))).save(
        obj_id=uid,
        payload=data,
        params=params
    )
    if self.verbose and not info.get('error'):
      eprint('project', uid, 'updated')
    return info

  ################################################################################################
  ### SAMPLE #####################################################################################
  ################################################################################################
  def create_sample(self, data, source='api', upload=True): # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    '''Create sample with the provided info

    Parameters
    ----------
    data : dict
        Dictionary of sample information.

    source : str
        TODO

    upload : bool
        Whether to upload the sample to the server or not.

    '''

    # get api version
    prefix = self.conf.get('api', {}).get('prefix', '/api/v2/')

    # some input validation
    data['genome'] = self._get_genome_by_name(data.get('genome'))

    if data.get('default_workflow'):
      if not self._check_workflow(data['default_workflow']):
        del data['default_workflow']
        eprint('Provided workflow is not valid.')

    if 'filepaths1' in data and data['filepaths1'] is None:
      if self.verbose:
        eprint('filepaths1 is None.')
      del data['filepaths1']

    if 'filepaths2' in data and data['filepaths2'] is None:
      if self.verbose:
        eprint('filepaths2 is None.')
      del data['filepaths2']

    # if only one sample as str, but into list
    if data.get('filepaths1') and isinstance(data['filepaths1'], str):
      data['filepaths1'] = [data['filepaths1']]

    if data.get('filepaths2') and isinstance(data['filepaths2'], str):
      data['filepaths2'] = [data['filepaths2']]

    if data.get('filepaths2') and not data.get('filepaths1'):
      eprint('ERROR: Parameter filepaths1 cannot be empty if filepaths2 is specified.')
      return None

    # validate unique file between filepaths1 and filepaths2
    does_repeast = data.get('filepaths2') \
      and any(path in data.get('filepaths2') for path in data.get('filepaths1'))
    if does_repeast:
      eprint('ERROR: Same file cannot be use in filepaths1 and filepaths2.')
      return None

    if data.get('default_workflow'):
      data['default_workflow'] = '{}pipelines/{}'.format(prefix, data['default_workflow'])

    if data.get('projects'):
      project = (Project(self.conf.get('api'))).get(data.get('projects'))
      if project.get('error'):
        eprint('ERROR: Looking for project. {}'.format(project.get('msg')))
        return None
      data['projects'] = [project.get('resource_uri')]

    info = (Sample(self.conf.get('api'))).save(payload=data)
    sample_id = info.get('id')

    if self.verbose == 2:
      eprint('Creating sample:')
      eprint('Data:', data)

    if sample_id:  # success
      if self.verbose:
        eprint('created: sample with id', sample_id)
    else:  # failure
      eprint('failed sample creation:', data['name'], info.get('msg'))
      return None

    # do the actual upload, update filepath
    files_to_upload = []
    for path in data.get('filepaths1', []):
      path = os.path.abspath(os.path.expanduser(
          os.path.expandvars(path)
      ))
    for path in data.get('filepaths2', []):
      path = os.path.abspath(os.path.expanduser(
          os.path.expandvars(path)
      ))

    # if a sample id exists, then upload the files
    if self.verbose:
      eprint('Sample id: {}'.format(sample_id))

    order = 0
    all_files = data.get('filepaths1', []) + data.get('filepaths2', [])
    for filepath in all_files:
      if self.verbose:
        eprint('Creating upload {}'.format(filepath))

      upload_id, filepath, key = self.create_upload(
          sample_id,
          filepath,
          order,
          is_paired_end=filepath in data.get('filepaths2', []),
          source=source
      )
      files_to_upload.append([upload_id, filepath, key])
      order += 1

    if upload:
      for upload_id, filepath, key in files_to_upload:
        if self.verbose:
          eprint('Uploading. upload_id: {}, filepath: {}, key: {}'.format(
              upload_id,
              filepath,
              key
          ))
        self.upload_file(upload_id, filepath, key)
    return sample_id

  def delete_sample(self, uid):
    '''Delete method'''
    info = (Sample(self.conf.get('api'))).delete(uid)
    if info.get('error'):
      eprint('error: deleting {}, msg: {}'.format(uid, info.get('msg')))
      return None

    if self.verbose:
      eprint('deleted sample', uid)
    return info

  def get_sample(self, uid, add_analysis=True):
    '''Get resource'''
    info = (Sample(self.conf.get('api'))).get(
        uid,
        cache='{}/json/sample.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )
    if info and add_analysis:
      info = self._add_full_analysis(info)
    return info

  def get_sample_owner(self, sample_id):
    '''Get sample owner'''
    user_id = self._get_sample_owner_id(sample_id)
    return self.get_user(user_id) if user_id else None

  def get_samples(self, filters={}): # pylint: disable=dangerous-default-value
    '''Get resource list'''
    return (Sample(self.conf.get('api'))).list_all(filters=filters)

  def samples_by_name(self, name, project_id=None):
    '''Get sample id from name'''
    return (Sample(self.conf.get('api'))).by_name(name, project_id)

  def update_sample(self, uid, data):
    '''Update resource'''
    genome = data.get('genome')
    if genome:
      data['genome'] = self._get_genome_by_name(genome)

    info = (Sample(self.conf.get('api'))).save(obj_id=uid, payload=data)
    if self.verbose and not info.get('error'):
      eprint('sample', uid, 'updated')
    return info

  ################################################################################################
  ### UPLOAD #####################################################################################
  ################################################################################################
  def create_upload(self, sample_id, filepath, order, is_paired_end, source='api', uri=None): # pylint: disable=too-many-arguments
    '''Create a upload object and actually upload the file'''
    prefix = self.conf.get('api', {}).get('prefix', '/api/v2/')
    filesize = None
    key = filepath
    status = 'in_progress'
    if filepath.startswith('ftp://') or uri:
      status = 'completed'
    else:
      key = 'uploads/{}/{}/{}'.format(
        self.conf['user']['id'],
        sample_id,
        os.path.basename(filepath)
      )
      filesize = os.stat(filepath).st_size if os.path.exists(filepath) else 0

    # update record with location of uploaded file
    info = (Upload(self.conf.get('api'))).save(payload={
        'filesize': filesize,
        'is_paired_end': is_paired_end,
        'key': key,
        'order': order,
        'sample': '{}samples/{}'.format(prefix, sample_id),
        'source': source,
        'status': status,
        'uri': uri,
        # 'timetaken': seconds_to_upload,
    })
    upload_id = info.get('id')
    if upload_id:
      if self.verbose:
        eprint('\tcreated: upload with id', upload_id)
      return upload_id, filepath, key
    return None, None, None

  def delete_upload(self, uid):
    '''Delete method'''
    return (Upload(self.conf.get('api'))).delete(uid)

  def get_upload(self, uid):
    '''Get resource'''
    return (Upload(self.conf.get('api'))).get(
      uid,
      cache='{}/json/upload.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )

  def get_uploads(self, params={'limit': 0}): # pylint: disable=dangerous-default-value
    '''Get resource list'''
    info = (Upload(self.conf.get('api'))).list(
        params=params
    )
    return info.get('objects', [])

  def update_upload(self, uid, data):
    '''Update resource'''
    return (Upload(self.conf.get('api'))).save(obj_id=uid, payload=data)

  def upload_file(self, upload_id, filepath, key):
    '''Upload file to S3 and update info'''
    starttime = time.time()
    response = self.copy_file(filepath, key, action='to')
    seconds_to_upload = int(time.time() - starttime)
    (Upload(self.conf.get('api'))).save(obj_id=upload_id, payload={
        'filesize': os.stat(filepath).st_size,
        'seq_length': 0,
        'status': 'completed' if response else 'failed',
        'timetaken': seconds_to_upload,
    })

  def upload_uri_to_id(self, uri):
    '''Get upload from uri and return upload id'''
    response = (Upload(self.conf.get('api'))).list({'limit': 2, 'uri': uri})
    items = response.get('objects')
    if not items:
      eprint('WARNING: no upload by uri', uri)
      return None
    if len(items) > 1:
      eprint('WARNING: multiple upload by uri', uri)
    return items[0].get('id')

  ################################################################################################
  ### USER #######################################################################################
  ################################################################################################
  def get_user(self, uid):
    '''Get resource'''
    return (User(self.conf.get('api'))).get(
        uid,
        cache='{}/json/user.{}.json'.format(self.scratch, uid) if self.use_cache else False,
    )

  ################################################################################################
  ### GENERAL HELPERS AND METHODS ################################################################
  ################################################################################################
  def copy_file(self, src, dest, action='to'):
    '''Copy file'''
    return self.copy_file_to_s3(src, dest) if action == 'to' \
        else self.copy_file_from_s3(src, dest)

  def copy_file_from_s3(self, src, dest):
    '''
    Low level function to copy a file from cloud to disk
    Parameters
    ----------
    src:  {str} File path on AWS S3, not including the bucket           [Required]
    dest: {str} Directory or file path where file will be downloaded to [Required]
    '''
    storage_cfg = self.configuration.get_user_storage()
    if not src.startswith('s3://'):
      src = 's3://{}/{}'.format(storage_cfg.get('bucket'), src)
    cmd = self.get_copy_cmd(src, dest)
    if self.verbose:
      eprint('copying from {} to {}'.format(src, dest))
    return self._execute_command(cmd=cmd, retry=3)

  def copy_file_to_s3(self, src, dest, params=None):
    '''Low level function to copy a file to cloud from disk'''
    storage_cfg = self.configuration.get_user_storage()
    dest = 's3://{}/{}'.format(storage_cfg.get('bucket'), dest)
    cmd = self.get_copy_cmd(src, dest, sse=True, params=params)
    if self.verbose:
      eprint('copying from {} to {}'.format(src, dest))
    return self._execute_command(cmd=cmd)

  def download_file(self, filekey, filename=None, dirname=None, is_json=False, load=False): # pylint: disable=too-many-arguments
    '''
    High level function, downloads to scratch dir and opens and
    parses files to JSON if asked. Uses low level copy_file()
    Parameters
    ----------
    filekey:  {str}   The full file path on AWS S3               [Required]
    dirname:  {str}   Directory to download the file to
    filename: {str}   Give the download file a new name
    isjson:   {bool}  Whether the downloaded file is JSON format
    load:     {bool}  Load the file after downloading
    Returns
    -------
    Absolute filepath to downloaded file
    '''

    if not filename:
      # don't renaming the file
      # get the download directory
      prefix = self.scratch
      if dirname:
        prefix = dirname if dirname.startswith('/') else os.path.join(self.scratch, dirname)
      filepath = os.path.join(prefix, os.path.basename(filekey))
    else:
      # rename the download file
      filepath = self.get_filepath(filename, dirname=dirname)
    filepath = os.path.expanduser(filepath)

    # if file not already there, download it
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
      if self.verbose:
        eprint('downloading', filepath)
      if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
      self.copy_file(filekey, filepath, action='from')
    elif self.verbose:
      eprint('exists', filepath)

    if load:
      data = open(filepath, 'r').read().strip()
      return json.loads(data) if is_json else data
    return filepath

  def download_raw_files(self, sample, outdir=None):
    '''
    Download raw data associated with a sample
    Parameters
    ----------
    sample: {dict} From calling bp.get_sample()       [Required]
    outdir: {str}  Output directory to save files to
    '''
    uploads = sample['uploads']
    files = [(upload.get('uri') or upload.get('key')) for upload in uploads]
    files_downloaded = []
    for file_i in files:
      outdir = outdir if outdir else self.scratch
      fileout = os.path.join(outdir, os.path.split(file_i)[1])
      if os.path.exists(fileout):
        eprint('Not downloading. File exists: {}'.format(fileout))
        output = True
      else:
        output = self.copy_file_from_s3(file_i, outdir)

      if output:
        eprint('Downloaded {} to {}.'.format(os.path.split(file_i)[1], outdir))
        files_downloaded.append(fileout)
    return files_downloaded

  @classmethod
  def filter_files_by_tags(cls, files, tags, exclude=None, kind='exact', multiple=False): # pylint: disable=too-many-arguments
    '''
    Filter files that have all the tags. If exclude tags provided,
    only return the files that don't have the exclude tags.append
    In some cases, multiple files are expected, set it to true.
    Parameters
    ---------
    files:    {dict}  List dictionaries containing file information     [Required]
    tags:     {list}  List of tags                                      [Required]
    kind:     {str}   Type of tag filtering. Options: exact, subset
    exclude:  {list}  List of tags to exclude
    multiple: {bool}  Whether to return all matching files or only one
    Returns
    -------
    A list of files
    '''

    if tags is None:
      return files

    if not isinstance(tags, list):
      eprint('Invalid tags argument. Provide a list of tags.')
      return None

    # filter for matches
    files = [
      file for file in files if file['tags'] and getattr(SetFilter, kind)(tags, file['tags'])
    ]

    # exclude files by tag
    if exclude:
      files = [
        file for file in files if file['tags'] and SetFilter.diff(file['tags'], exclude)
      ]

    # check if no files left after filtering
    if len(files) == 0:
      eprint('No matching files after filtering by tags:', tags)
      return None

    # return files
    if multiple:
      return files
    if len(files) > 1:
      eprint('multiple matches for tags:', tags)
      return files[0:1]
    return files

  def get_analysis_files(self, analysis, dirname=None, kind='exact', tags=None):  # pylint: disable=too-many-arguments
    '''
    For a analysis, go through files and get that match the tags
    Parameters
    ----------
    analysis: {dict}  The dictionary returned by bp.get_analysis()  [Required]
    dirname:  {str}   Directory to download files to
    kind:     {str}   Type of tag filtering. Options: exact, subset
    tags:     {list}  List of lists of tags to filter by
    '''
    # some input checking
    if tags:
      is_not_valid = not (isinstance(tags, list) and all((isinstance(item, list) for item in tags)))
      if is_not_valid:
        eprint('Invalid tags argument. Provide a list of list of tags.')
        return None
    else:
      tags = [None]

    # filter the files
    matching_files = []
    for tags_sub in tags:
      files = self.filter_files_by_tags(
        analysis['files'],
        tags_sub,
        kind=kind,
        multiple=True,
      )
      if files:
        matching_files += files

    return [self.download_file(
      matching_file['path'],
      dirname=dirname,
    ) for matching_file in matching_files] if matching_files else None

  def get_bam_file(self, sample, tags=None, multiple=False):
    '''Get bam file. If you want deduped bam file, call with tags = ['bam', 'dedup']'''
    return self.get_file_by_tags(
      sample,
      analysis_tags=['alignment'],
      multiple=multiple,
      tags=tags if tags else ['bam'],
    )

  def get_bigwig_file(self, sample, multiple=False):
    '''Get bigwig file - for ChIP-Seq'''
    return self.get_file_by_tags(
      sample,
      analysis_tags=['alignment'],
      kind='exact',
      multiple=multiple,
      tags=['bigwig'],
    )

  def get_copy_cmd(self, src, dest, sse=False, params=None):
    '''
    Create copy cmd based on AWS cli utility
    Parameters
    ----------
    src:    {str}     Path to file on AWS S3                                          [Required]
    dest:   {str}     Destination directory or path where file will be downloaded to  [Required]
    sse:    {bool}    Whether to use sever side encryption
    params: {dict}    Other download paramters
    '''
    _params = ''
    if sse:
      _params = '--sse'
    if params:
      for arg, val in params.items():
        _params += ' {} "{}"'.format(arg, val)

    storage_cfg = self.configuration.get_user_storage()
    credential = self.configuration.get_cli_credentials_from(storage_cfg)
    return '{}aws s3 cp "{}" "{}" {}'.format(credential, src, dest, _params)

  def get_expression_count_file(self, sample, features='transcripts', multiple=False):
    '''Get expression count text file - for RNA-Seq'''
    tags = ['expression_count', 'by_transcript', 'text']
    if features == 'genes':
      tags = ['expression_count', 'by_gene', 'text']
    if self.verbose:
      eprint('getting file w tags', tags)
    return self.get_file_by_tags(
      sample,
      analysis_tags=['alignment'],
      kind='exact',
      multiple=multiple,
      tags=tags,
    )

  def get_file_by_node(
    self,
    sample,
    analysis_tags=None,
    dest=None,
    dirname=None,
    multiple=False,
    node=None,
  ): # pylint: disable=too-many-arguments,too-many-branches,too-many-locals
    '''For a sample, go through analysis and get files that match the tags'''
    matches = []
    for analysis in sample['analyses_full']:
      should_continue = analysis['status'] == 'error' or (analysis_tags and not (
        analysis['tags'] and (set(analysis_tags) <= set(analysis['tags']))
      ))
      if should_continue:
        continue

      matching_file = self._filter_files_by_node(
          analysis['files'], node, multiple=multiple)

      if matching_file:
        if multiple:
          for file in matching_file:
            matches.append([analysis['id'], file])
        else:
          matches.append([analysis['id'], matching_file])

    if len(matches) == 0:
      eprint('WARNING: no matching file for', node)
      return None

    if len(matches) > 1:
      matches.sort(
        key=lambda match: datetime.datetime.strptime(match[1]['last_updated'], '%Y-%m-%dT%H:%M:%S.%f'),
        reverse=True,
      )
      if not multiple:
        eprint('WARNING: multiple matching file for', node)
      for match in matches:
        eprint('\t', match[1]['last_updated'], match[1]['path'])

    filepath = []
    for match in matches:
      path = self.download_file(match[1]['path'], filename=dest, dirname=dest) if dest \
        else self.download_file(match[1]['path'], dirname=dirname)

      # if did download it then we added to the filepath else continue
      if os.path.isfile(path):
        filepath.append(path)
        if not multiple:
          break
    else:
      filepath.append(match[1]['path'])

    return filepath if multiple else filepath[0]

  def get_file_by_tags(
    self,
    sample,
    analysis_tags=None,
    dest=None,
    dirname=None,
    download=True,
    exclude=None,
    kind='exact',
    multiple=False,
    tags=None,
    #workflow_id=None,
  ): # pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-statements
    '''
    For a sample, go through analysis and get files that match the tags.
    Parameters
    ----------
    sample:        {dict} Sample information                                       [Required]
    analysis_tags: {list} Analysis tags to filter analyses when looking for files
    dest:          {str}  File name to save the file to
    dirname:       {str}  Ouput directory to save the file to
    download:      {bool} Whether to download the file(s)
    exclude:       {list} List of tags to exclude
    kind:          {str}  Type of tag filtering to do. Options: exact, diff, or subset
    multiple:      {bool} Whether to return multiple files or just the first one
    tags:          {list} List of list of tags for file filtering. If just list of tags, will convert to list of lists.
    workflow_id:   {int}  Workflow id to look for files in. NOT IMPLEMENTED YE
    '''
    # some error checking
    if tags is None:
      eprint("Tags is None")
      return None

    # make sure tags is a list of lists
    if isinstance(tags, list):
      if not isinstance(tags[0], list):
        tags = [tags]

    matches = []
    matching_file = []
    for analysis in sample['analyses_full']:
      if analysis['status'] == 'error':
        eprint('analysis ended in error, skipping.')
        continue

      # dont even look if not the right type of analysis
      should_continue = analysis_tags and not(
        analysis['tags'] and set(analysis_tags) <= set(analysis['tags'])
      )
      if should_continue:
        continue

      if analysis['params'] and 'info' in analysis['params']:
        if not analysis['params']['info'].get('genome_id'):
          eprint('Could not find genome for analysis {}'.format(analysis['id']))
          continue
        sample_genome_id = self.get_id_from_url(sample.get('genome', ''))
        if not sample_genome_id:
          eprint('Could not find genome for analysis {}'.format(analysis['id']))
          continue
        if int(analysis['params']['info']['genome_id']) != int(sample_genome_id):
          eprint(
            'analysis genome {}'.format(analysis['params']['info']['genome_id']),
            'different from sample genome {}.'.format(sample_genome_id),
          )
          continue

      if self.verbose:
        eprint('looking at', analysis['id'], 'status', analysis['status'])
      for tags_sub in tags:
        filtered_files = self.filter_files_by_tags(
          analysis['files'],
          tags_sub,
          exclude=exclude,
          kind=kind,
          multiple=multiple,
        )

        if filtered_files:
          matching_file += filtered_files

      if matching_file:
        if multiple:
          for file in matching_file:
            matches.append([analysis['id'], file])
        else:
          matches.append([analysis['id'], matching_file[0]])

    if not matches:
      eprint('WARNING: no matching file for', tags)
      eprint('in analyses with ids', [analysis['id'] for analysis in sample['analyses_full']])
      eprint('for sample', sample['id'])
      return None

    if len(matches) > 1:
      matches.sort(
        key=lambda match: datetime.datetime.strptime(match[1]['last_updated'], '%Y-%m-%dT%H:%M:%S.%f'),
        reverse=True,
      )
      if not multiple:
        eprint('WARNING: multiple matching file for', tags)
      for match in matches:
        eprint('\t', match[1]['last_updated'], match[1]['path'])


    filepath = []
    for match in matches:
      if download:
        path = self.download_file(match[1]['path'], filename=dest, dirname=dest) if dest \
          else self.download_file(match[1]['path'], dirname=dirname)

         # if did download it then we added to the filepath else continue
        if os.path.isfile(path):
          filepath.append(path)
          if not multiple:
            break
      else:
        filepath.append(match[1]['path'])

    return filepath if multiple else filepath[0]

  def get_filepath(self, filename, dirname=None):
    '''Use scratch and [dirname] to construct a full filepath'''
    # move along, nothin to do
    if filename.startswith('/'):
      filepath = filename
    else:
      if dirname:
        filename = '{}/{}'.format(dirname.rstrip('/'), filename)
      # adding dirname made it full
      filepath = filename if filename.startswith('/') else self.scratch + '/' + filename
    return filepath

  def get_history(self, analysis_id, outdir=None):
    '''
    Get SWF history for the analysis
    Parameters
    ----------
    analysis_id: {int} Analysis ID                                      [Required]
    outdir:      {str} Directory to save data. Use instead of scratch.
    '''
    user_id = self._get_analysis_owner_id(analysis_id)
    filekey = 'log/analyses/{}/{}/history.json'.format(user_id, analysis_id)
    filename = '{}/history/history.{}.json'.format(
      outdir if outdir else self.scratch,
      analysis_id
    )
    return self.download_file(filekey, filename, load=True, is_json=True)

  def get_id_from_url(self, url):
    '''Parse URL to get the id'''
    return self.parse_url(url)['id']

  def get_log(self, analysis_id, outdir=None):
    '''
    Get log file for the analysis
    Parameters
    ----------
    analysis_id: {int} Analysis ID                                      [Required]
    outdir: {str}      Directory to save data. Use instead of scratch.
    '''
    user_id = self._get_analysis_owner_id(analysis_id)
    filekey = 'log/analyses/{}/{}/worker.log'.format(user_id, analysis_id)
    filename = '{}/worker.{}.log'.format(outdir if outdir else self.scratch, analysis_id)
    return self.download_file(filekey, filename, load=False, is_json=False)

  def get_window_score_filename(self, sample, kind=None, flanking=None):
    '''Get window score filename'''
    suffix = 'score-{}-{}Kb'.format(kind, flanking / 1e3)
    suffix = suffix.replace('.0Kb', 'Kb')
    return '{}/score/{}.{}.dedup.{}.txt'.format(
      self.scratch,
      sample['slug'],
      sample['genome'],
      suffix,
    )

  @classmethod
  def parse_url(cls, url):
    '''Parse URL to get the id, and other stuff'''
    parts = url.rsplit('/', 1)
    return {'id': parts[1]}

  def print_data(self, data_type='', is_json=False, uid=None, project=None):
    '''
    Print data associated with genomes, samples, etc..
    Parameters
    ----------
    data_type: {str}   Type of data to print (e.g. workflows)
    is_json:      {bool}  By default, data is printed in a human-readable format
    uid:       {list}  One or more ids of the objects you want
    project: {int} project id to filter data
    '''

    if not isinstance(uid, list):
      uid = [uid]

    detail_methods = {
      'analysis': 'get_analysis',
      'genome': 'get_genome',
      'sample': 'get_sample',
    }

    list_methods = {
      'analyses': 'get_analyses',
      'genomes': 'get_genomes',
      'samples': 'get_samples',
      'workflows': 'get_workflows',
    }

    # get the appropriate data
    data = []

    # if it is a detail
    if data_type in detail_methods:
      if uid is None:
        eprint('Your uid is invalid: {}'.format(uid))
        return

      for item_id in uid:
        data_tmp = getattr(self, detail_methods.get(data_type))(item_id)
        if data_tmp.get('id'):
          data.append(data_tmp)
        else:
          eprint('{} with uid {} invalid.'.format(data_type.capitalize(), item_id))

    filters = {}
    if project:
      filters['projects__exact'] = project

    # if it is a list
    if data_type in list_methods:
      data = getattr(self, list_methods.get(data_type))(filters=filters)

    if not data:
      eprint('No data found for the parameters you gave.')
      return

    if isinstance(data, dict) and data.get('error'):
      eprint(data.get('msg', 'Error retrieving data.'))
      return

    # print the data as json
    if is_json:
      for item in data:
        eprint(item)
        eprint()
      return

    # print the data human readable
    getattr(NicePrint, data_type)(data)

  ### Private methods ###
  def _add_full_analysis(self, sample):
    '''Add full analysis info to the sample'''
    analysis_ids = [self.parse_url(uri)['id']
        for uri in sample.get('analyses', [])]
    analyses = [self.get_analysis(uid) for uid in analysis_ids]
    # remove null analyses, probably deleted or no ownership
    analyses = [analysis for analysis in analyses if not analysis.get('error')]
    # sort them by latest updated
    analyses.sort(
      key=lambda analysis: datetime.datetime.strptime(analysis.get('last_updated'), '%Y-%m-%dT%H:%M:%S.%f'),
      reverse=True,
    )
    sample['analyses_full'] = analyses
    return sample

  def _check_sample(self, uid):
    '''Check if the sample is in the Basepair database'''
    info = self.get_sample(uid, add_analysis=False)
    if info.get('id'):
      return True
    eprint('The provided sample id: {id}, does not exist in Basepair.'.format(id=uid))
    return False

  def _check_workflow(self, uid):
    '''Check if the workflow is in the Basepair database'''
    info = self.get_workflow(uid)
    if info.get('id'):
      return True
    eprint('The provided workflow id: {id}, does not exist in Basepair.'.format(id=uid))
    return False

  def _execute_command(self, cmd=None, retry=5, current_try=0):
    '''Execute s3 commands'''
    sleep_time = 3
    try:
      if self.verbose:
        eprint('Executing command:  {}\n'.format(cmd))
      return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except CalledProcessError as error:
      eprint('Error: {}'.format(error.output))
      eprint('Return code: {}'.format(error.returncode))
      if current_try >= retry:
        return None
      eprint('retrying in {} seconds...'.format(sleep_time))
      time.sleep(sleep_time)
      return self._execute_command(cmd=cmd, current_try=current_try + 1)

  @classmethod
  def _filter_files_by_node(cls, files, node, multiple=False):
    '''Filter files that are from the node.'''
    # In some cases, multiple files are expected, set it to true.
    files = [file for file in files if file['node'] == node]
    if multiple:
      return files
    if not files:
      return None
    if len(files) > 1:
      eprint('multiple matches for node:', node)
    return files[0]

  def _get_analysis_owner_id(self, analysis_id):
    '''Get analysis owner id'''
    info = self.get_analysis(analysis_id)
    return self.parse_url(info['owner'])['id'] if info else None

  def _get_genome_by_name(self, genome_name):
    '''Check if the genome is in the Basepair database'''
    if genome_name:
      available_genomes = [item for item in self.genomes if item.get('name') == genome_name]
      if not available_genomes:
        eprint(
          'The provided genome, {}, does not exist in Basepair. Proceeding anyway...'.format(genome_name)
        )
        return None
      return available_genomes[0].get('resource_uri')
    return None

  def _get_sample_owner_id(self, sample_id):
    '''Get sample owner id'''
    info = self.get_sample(sample_id)
    return self.parse_url(info['owner'])['id'] if info else None

  def _get_user_id(self):
    '''Get userid, username provided in conf'''
    user = (User(self.conf.get('api'))).list(
      params={'limit': 1, 'username': self.conf['api']['username']}
    )
    self.conf['user'] = user.get('objects', [None])[0]

  @classmethod
  def _parsed_sample_list(cls, items, prefix):
    '''Parse sample id list into sample resource uri list'''
    return ['{}samples/{}'.format(prefix, item_id) for item_id in items]
