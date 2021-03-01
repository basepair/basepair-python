'''Helper to print object nicely'''
from __future__ import print_function

# General imports
import os

# Lib imports
from tabulate import tabulate

class NicePrint:
  '''Helper class to print nice objects'''

  @staticmethod
  def analyses(data):
    '''Print analyses'''
    to_print = [
      [
        analysis['id'],
        analysis['name'],
        analysis['started_on'],
        analysis['completed_on'],
        analysis['status'],
        analysis['meta']['num_files'],
        analysis['tags']
      ] for analysis in data
    ]
    print(tabulate(to_print, headers=[
      'id',
      'name',
      'started on',
      'completed on',
      'status',
      'num files',
      'tags',
    ]))

  @staticmethod
  def analysis(data):
    '''Print analysis'''
    for analysis in data:
      to_print = [
        ['id', analysis['id']],
        ['name', analysis['name']],
        ['date_created', analysis['date_created']],
        ['completed_on', analysis['completed_on']],
      ]

      for sample in analysis['samples']:
        to_print.append(['sample', sample.split('/')[-1]])

      if analysis['controls']:
        for control in analysis['controls']:
          to_print.append(['control', control['id']])

      print('\nAnalysis info:')
      print(tabulate(to_print, headers=['Variable', 'Value']))

      print('\nAnalysis files:')

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
      print(tabulate(
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
      print('\n\n')

  @staticmethod
  def genome(data):
    '''Print genome'''
    to_print = [[genome['id'], genome['name'], genome['created_on']] for genome in data]
    print(tabulate(to_print, headers=['id', 'name', 'created_on']))

  @staticmethod
  def genomes(data):
    '''Print genomes'''
    NicePrint.genome(data)

  @staticmethod
  def sample(data):
    '''Print sample'''
    for sample in data:
      print('Sample id: {}'.format(sample['id']))
      print('Sample name: {}'.format(sample['name']))
      print('Sample datatype: {}'.format(sample['datatype']))
      print('Sample genome: {}'.format(sample['genome_name'] or sample['genome']))
      print('Sample data created: {}'.format(sample['date_created']))
      print('Sample num reads: {}'.format(sample['meta']['num_reads']))
      print('Analyses:')
      to_print = [
        [
          analysis['id'],
          analysis['name'],
          analysis['started_on'],
          analysis['completed_on'],
          analysis['status'],
          analysis['meta']['num_files'],
          analysis['tags']
        ] for analysis in sample['analyses_full']
      ]
      print(tabulate(to_print, headers=[
        'id',
        'name',
        'started on',
        'completed on',
        'status',
        'num files',
        'tags',
      ]))
      print('\n\n')

  @staticmethod
  def samples(data):
    '''Print samples'''
    to_print = [
      [
        sample['id'],
        sample['name'],
        sample['datatype'],
        sample['genome_name'] or sample['genome'],
        sample['date_created'],
        sample['meta']['num_reads']
      ] for sample in data
    ]
    print(tabulate(to_print, headers=[
      'id',
      'name',
      'datatype',
      'genome',
      'date created',
      'num reads',
    ]))

  @staticmethod
  def workflows(data):
    '''Print pipelines'''
    to_print = [
      [
        pipeline['id'],
        pipeline['name'],
        pipeline['datatype'],
        pipeline['description'],
        pipeline['tags']
      ] for pipeline in data
    ]
    print(tabulate(to_print, headers=[
      'id',
      'name',
      'datatype',
      'description',
      'tags',
    ]))
