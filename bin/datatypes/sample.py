'''Sample datatype class'''
import sys
# App imports
from basepair.helpers import eprint
from bin.common_parser import add_json_parser, add_common_args, add_single_uid_parser, \
add_uid_parser, add_outdir_parser, add_payload_args, add_tags_parser, valid_uid

class Sample:
  '''Sample action methods'''

  @staticmethod
  def create_sample(bp_api, args):
    '''Create sample'''
    try:
      data = {
        'datatype': args.type,
        'default_workflow': int(args.pipeline) if args.pipeline else None,
        'filepaths1': args.file1,
        'filepaths2': args.file2,
        'genome': args.genome,
        'name': args.name,
        'platform': args.platform,
        'projects': int(args.project) if args.project else None,
      }

      if args.key and args.val:
        for key, val in zip(args.key, args.val):
          data[key] = val
      bp_api.create_sample(data, upload=True, source='cli')
    except:
      sys.exit('ERROR: sample creation failed. Please try again!')

  @staticmethod
  def delete_sample(bp_api, args):
    '''Delete sample'''
    uids = args.uid
    for uid in uids:
      answer = bp_api.yes_or_no('Are you sure you want to delete {}?'.format(uid))
      if answer:
        bp_api.delete_sample(uid)
    return

  @staticmethod
  def download_sample(bp_api, args):
    '''Download sample'''
    for uid in args.uid:
      # check sample id is valid
      sample = bp_api.get_sample(uid, add_analysis=True)
      if sample.get('error'):
        continue
      else:
        # if tags provided, download file by tags
        if args.tags:
          bp_api.get_file_by_tags(sample, tags=args.tags,kind=args.tagkind, dirname=args.outdir)
        else:
          bp_api.download_raw_files(sample, args.outdir)
    return

  @staticmethod
  def get_sample(bp_api, args):
    '''Get sample'''
    uids = args.uid
    is_json = args.json
    for uid in uids:
      bp_api.print_data(data_type='sample', uid=uid, is_json=is_json)
    return

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

    if args.key and args.val:
      for key, val in zip(args.key, args.val):
        if key in ['adapter', 'amplicon', 'barcode', 'regions', 'stranded']:
          data['info'] = data.get('info', {})
          data['info'][key] = val  # set sample info field

    res = bp_api.update_sample(args.uid, data)
    return

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
        'panel', 'rna-seq', 'scrna-seq', 'small-rna-seq', 'snap-chip', 'wes', 'wgs'
      ],
      default='rna-seq'
    )
    create_sample_p.add_argument('--file1', nargs='+', required=True)
    create_sample_p.add_argument('--file2', nargs='+')
    create_sample_p.add_argument('--genome')
    create_sample_p.add_argument('--key', action='append')
    create_sample_p.add_argument('--name')
    create_sample_p.add_argument('--platform')
    create_sample_p.add_argument('--project', help='Project id', type=valid_uid)
    create_sample_p.add_argument('--val', action='append')
    create_sample_p.add_argument('--pipeline', help='Pipeline id', type=valid_uid)
    create_sample_p = add_common_args(create_sample_p)

    # delete sample parser
    delete_sample_p = action_parser.add_parser(
      'delete',
      help='delete a sample.'
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
        'panel', 'rna-seq', 'scrna-seq', 'small-rna-seq', 'snap-chip', 'wes', 'wgs'
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
