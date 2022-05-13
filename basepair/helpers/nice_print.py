'''Helper to print object nicely'''
from __future__ import print_function

# General imports
import os

# Lib imports
from tabulate import tabulate

# App imports
from basepair.helpers import eprint

class NicePrint:
  '''Helper class to print nice objects'''

  @staticmethod
  def analyses(data):
    '''Print analyses'''
    headers = [
      'id',
      'name',
      'started_on',
      'completed_on',
      'status',
      'tags',
    ]
    to_print = [[analysis[field] for field in headers] for analysis in data]
    eprint(tabulate(to_print, headers=[header.replace('_', ' ') for header in headers]))

  @staticmethod
  def analysis(data):
    '''Print analysis'''
    for analysis in data:
      fields = ['id', 'name', 'date_created', 'completed_on']
      to_print = [[field, analysis[field]] for field in fields]

      for sample in analysis['samples']:
        to_print.append(['sample', sample['id']])

      if analysis['controls']:
        for control in analysis['controls']:
          to_print.append(['control', control['id']])

      eprint('\nAnalysis info:')
      eprint(tabulate(to_print, headers=['Variable', 'Value']))

      eprint('\nAnalysis files:')

      # convert only filesizes that are not None
      for filedata in analysis['files']:
        filedata['filesize'] = filedata['filesize']/(1024.**3) if filedata['filesize'] else 'NA'

      bucket = analysis.get('params', {}).get('info', {}).get('bucket', None)
      to_print = [
        [
          file['id'],
          file['filesize'],
          file['source'],
          os.path.split(file['path'])[1],
          '{}{}'.format('s3://{}/'.format(bucket) if bucket else '', file['path']),
          file['tags'],
        ] for file in analysis['files']
      ]
      eprint(tabulate(
        to_print,
        floatfmt='.4f',
        headers=[
          'id',
          'filesize (Gigabytes)',
          'source',
          'name',
          'uri',
          'tags',
        ],
        numalign='right',
      ))
      eprint('\n\n')

  @staticmethod
  def genome(data):
    '''Print genome'''
    to_print = [[genome['id'], genome['name'], genome['created_on']] for genome in data]
    eprint(tabulate(to_print, headers=['id', 'name', 'created_on']))

  @staticmethod
  def genomes(data):
    '''Print genomes'''
    NicePrint.genome(data)

  @staticmethod
  def module(data):
    '''Print module'''
    headers = [
      'id',
      'name',
      'date_created',
      'visibility',
      'status'
    ]
    to_print = [[module[field] for field in headers] for module in data]
    eprint(tabulate(to_print, headers=[header for header in headers]))

  @staticmethod
  def pipeline_modules(data):
    '''Print modules of a pipeline'''
    headers = [
      'id',
      'name',
      'owner',
      'date_created'
    ]
    to_print = [[module[field] for field in headers] for module in data]
    eprint(tabulate(to_print, headers=[header for header in headers]))

  @staticmethod
  def sample(data):
    '''Print sample'''
    for sample in data:
      eprint('Sample id: {}'.format(sample['id']))
      eprint('Sample name: {}'.format(sample['name']))
      eprint('Sample datatype: {}'.format(sample['datatype']))
      eprint('Sample genome: {}'.format(sample['genome_name'] or sample['genome']))
      eprint('Sample data created: {}'.format(sample['date_created']))
      eprint('Sample num reads: {}'.format(sample['meta']['num_reads']))
      eprint('Analyses:')
      headers = [
        'id',
        'name',
        'started_on',
        'completed_on',
        'status',
        'tags',
      ]
      to_print = [[analysis[field] for field in headers] for analysis in sample['analyses_full']]
      eprint(tabulate(to_print, headers=[header for header in headers]))
      eprint('\n\n')

  @staticmethod
  def samples(data):
    '''Print samples'''
    headers = [
      'id',
      'name',
      'datatype',
      'genome',
      'date_created',
      'num_reads',
    ]
    to_print = [[sample['meta'][field] if field == 'num_reads' else sample[field] for field in headers] for sample in data]
    eprint(tabulate(to_print, headers=[header for header in headers]))

  @staticmethod
  def pipelines(data):
    '''Print pipelines'''
    headers = [
      'id',
      'name',
      'datatype',
      'description',
      'tags',
    ]
    to_print = [[pipeline[field] for field in headers] for pipeline in data]
    eprint(tabulate(to_print, headers=[header for header in headers]))

  @staticmethod
  def pipeline(data):
    '''Print pipelines'''
    headers = [
      'id',
      'name',
      'datatype',
      'description',
      'tags',
    ]
    to_print = [[pipeline[field] for field in headers] for pipeline in data]
    eprint(tabulate(to_print, headers=[header for header in headers]))

  @staticmethod
  def projects(data):
    '''Print projects'''
    headers = [
      'id',
      'name',
      'owner_fullname',
      'last_updated',
      'visibility',
    ]
    to_print = [[project[field] for field in headers] for project in data]
    eprint(tabulate(to_print, headers=[header.replace('_', ' ') for header in headers]))
