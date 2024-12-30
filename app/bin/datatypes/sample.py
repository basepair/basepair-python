'''Sample datatype class'''

# General Import
import os
import sys

# App imports
from basepair.helpers import eprint
from bin.common_parser import add_json_parser, add_common_args, add_single_uid_parser, \
add_uid_parser, add_outdir_parser, add_tags_parser, valid_uid, valid_sample_extensions , validate_sample_file

class Sample:
  '''Sample action methods'''

  @staticmethod
  def create_sample(bp_api, args):
    '''Create sample'''
    data = {
      'datatype': args.type,
      'default_workflow': int(args.pipeline) if args.pipeline else None,
      'filepaths1': args.file1 or [],
      'filepaths2': args.file2 or [],
      'genome': args.genome,
      'name': args.name,
      'platform': args.platform,
      'projects': int(args.project) if args.project else None,
    }
    # check if the files are all present
    not_found_msg = 'ERROR: Provided File: {} does not exists.'
    files = data['filepaths2'] + data['filepaths1']
    for file_name in files:
        if not os.path.isfile(file_name):
          sys.exit(not_found_msg.format(file_name))

    validate_sample_file(files)
    data['info'] = data.get('info', {})
    if args.key and args.val:
      for key, val in zip(args.key, args.val):
        data['info'][key] = val
    sample_id = bp_api.create_sample(data, upload=True, source='cli')
    if sample_id:
      eprint('Sample created successfully.')

  @staticmethod
  def delete_sample(bp_api, args):
    '''Delete sample'''
    uids = args.uid
    all_fail = True
    for uid in uids:
      answer = bp_api.yes_or_no('Are you sure you want to delete {}?'.format(uid))
      if answer:
        all_fail = not bool(bp_api.delete_sample(uid)) and all_fail
    if all_fail:
      sys.exit('ERROR: Deleting Sample(s) failed.')

  @staticmethod
  def download_sample(bp_api, args):
    '''Download sample'''
    all_fail = True
    for uid in args.uid:
      # check sample id is valid
      sample = bp_api.get_sample(uid, add_analysis=True)
      # if tags provided, download file by tags
      if args.tags:
        all_fail = not (bool(sample.get('id')) \
          and bp_api.get_file_by_tags(sample, file_type='samples', tags=args.tags, kind=args.tagkind, dirname=args.outdir, uid=uid)) \
          and all_fail
      else:
        all_fail = not (bool(sample.get('id')) \
          and bool(bp_api.download_raw_files(sample, file_type='samples', uid=uid, outdir=args.outdir))) \
          and all_fail

    if all_fail:
      sys.exit('ERROR: Downloading sample failed.')

  @staticmethod
  def get_sample(bp_api, args):
    '''Get sample'''
    all_fail = True
    for uid in args.uid:
      all_fail = not bool(bp_api.print_data(data_type='sample', uid=uid, is_json=args.json)) and all_fail
    if all_fail:
      sys.exit('ERROR: Sample data not found.')

  @staticmethod
  def update_sample(bp_api, args):
    '''Update sample'''
    data = {}
    if args.name:
      data['name'] = args.name

    if args.genome:
      data['genome'] = args.genome

    if args.type:
      data['datatype'] = args.type

    data['info'] = data.get('info', {})
    if args.key and args.val:
      for key, val in zip(args.key, args.val):
        if key in ['adapter', 'amplicon', 'barcode', 'regions', 'stranded']:
          data['info'][key] = val  # set sample info field

    if not data:
      sys.exit('ERROR: You have not provided any data to update.')
    bp_api.update_sample(args.uid, data)

  @staticmethod
  def list_sample(bp_api, args):
    '''List sample'''
    bp_api.print_data(data_type='samples', is_json=args.json, project=args.project)

  @staticmethod
  def sample_action_parser(action_parser):
    '''Sample parser'''

    # create sample parser
    create_sample_p = action_parser.add_parser(
      'create',
      help='Create a sample.'
    )
    create_sample_p.add_argument(
      '--type',
      choices=[
        'atac-seq', 'chip-seq', 'crispr', 'cutnrun', 'cutntag', 'dna-seq', 'other',
        'panel', 'rna-seq', 'scaleBio_scRNA', 'scrna-seq', 'small-rna-seq', 'snap-chip', 'wes', 'wgs'
      ],
      default='rna-seq'
    )
    example_key_usage = '''
      Example: basepair sample create --file example.bam --key name --val Alice --key age --val 30
    '''
    create_sample_p.add_argument('--file1', nargs='+', help='Available file types - {}'.format(' '.join(valid_sample_extensions)))
    create_sample_p.add_argument('--file2', nargs='+', help='Available file types - {}'.format(' '.join(valid_sample_extensions)))
    create_sample_p.add_argument('--genome', help='Name of the Genome')
    create_sample_p.add_argument('--key', action='append', help='Specify one(or more) key (can be used multiple times).\nShould be used along with --val flag.\nTags the sample with some additional information.')
    create_sample_p.add_argument('--name', help='Name of the sample')
    create_sample_p.add_argument('--platform', help='Name of the sequencing platform')
    create_sample_p.add_argument('--project', help='Project ID', type=valid_uid)
    create_sample_p.add_argument('--val', action='append', help='Specify one(or more)value corresponding to the key (must match number of --key).\nShould be used along with --key flag.' + example_key_usage)
    create_sample_p.add_argument('--pipeline', help='Pipeline ID', type=valid_uid)
    create_sample_p = add_common_args(create_sample_p)

    # delete sample parser
    delete_sample_p = action_parser.add_parser(
      'delete',
      help='Delete a sample.'
    )
    delete_sample_p = add_common_args(delete_sample_p)
    delete_sample_p = add_uid_parser(delete_sample_p, 'sample')

    # download sample parser
    download_sample_p = action_parser.add_parser(
      'download',
      help='Download one or more samples.'
    )
    download_sample_p = add_uid_parser(download_sample_p, 'sample')
    download_sample_p = add_tags_parser(download_sample_p)
    download_sample_p = add_outdir_parser(download_sample_p)
    download_sample_p = add_common_args(download_sample_p)

    # get sample parser
    get_sample_p = action_parser.add_parser(
      'get',
      help='List detail info about one or more samples.'
    )
    get_sample_p = add_common_args(get_sample_p)
    get_sample_p = add_uid_parser(get_sample_p, 'sample')
    get_sample_p = add_json_parser(get_sample_p)

    # update sample parser
    update_sample_parser = action_parser.add_parser(
      'update',
      help='Update information associated with a sample.'
    )
    update_sample_parser.add_argument(
      '--type',
      choices=[
        'atac-seq', 'chip-seq', 'crispr', 'cutnrun', 'cutntag', 'dna-seq', 'other',
        'panel', 'rna-seq', 'scaleBio-scRNA', 'scrna-seq', 'small-rna-seq', 'snap-chip', 'wes', 'wgs'
      ],
    )
    update_sample_parser.add_argument('--genome')
    update_sample_parser.add_argument('--key', action='append')
    update_sample_parser.add_argument('--name')
    update_sample_parser.add_argument('--val', action='append')
    update_sample_parser = add_common_args(update_sample_parser)
    update_sample_parser = add_single_uid_parser(update_sample_parser, 'sample')

    # list sample parser
    list_samples_p = action_parser.add_parser(
      'list',
      help='List basic info about all your samples.'
    )
    list_samples_p.add_argument(
      '--project',
      help='List samples of a project.',
      required=True,
      type=valid_uid
    )
    list_samples_p = add_common_args(list_samples_p)
    list_samples_p = add_json_parser(list_samples_p)

    return action_parser
