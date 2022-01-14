'''Analysis datatype class'''
from os import stat
import sys
# App Import
from bin.utils import update_info
from bin.common_parser import add_common_args, add_single_uid_parser, add_uid_parser, add_json_parser, add_tags_parser, add_outdir_parser
# App imports
from basepair.helpers import eprint


def verify_yaml(args):
  '''Verify yaml file'''
  if not args.test_pipeline and not args.test_modules:
    eprint('ERROR: at least one yaml file required.')
    return False
  if args.test_pipeline and len(args.test_pipeline) != 1:
    eprint('Please provide only one pipeline yaml')
    return False
  if args.test_modules:
    yaml_path = args.test_modules
    valid_extensions = ('.yaml', '.yml')
    for each_path in yaml_path:
      if each_path.endswith(valid_extensions):
        return True
    eprint('Please provide yaml file only')
    return False
  yaml_path = args.test_pipeline[0]
  valid_extensions = ('.yaml', '.yml')
  if yaml_path.endswith(valid_extensions):
    return True
  eprint('Please provide yaml file only')
  return False


class Analysis:
  '''Analysis action methods'''

  @staticmethod
  def get_analysis(bp_api, args):
    '''Get analysis'''
    uids = args.uid
    is_json = args.json
    if not uids:
      sys.exit('At least one uid required.')
    for uid in uids:
      bp_api.print_data(data_type='analysis', uid=uid, is_json=is_json)

  @staticmethod
  def create_analysis(bp_api, args):
    '''Create and submit an analysis'''
    params = {'node': {}}

    if args.test_modules or args.test_pipeline:
      result = verify_yaml(args)
      if not result:
        return

    if not args.test_pipeline and not args.workflow:
      sys.exit('ERROR: Pipeline required.')

    if not args.sample:
      sys.exit('ERROR: Minimum one sample required.')

    if args.params:
      for param in args.params:
        node_id, arg, val = param.split(':')
        if node_id not in params['node']:
          params['node'][node_id] = {}
        params['node'][node_id][arg] = val
    else:
      sys.exit('You specified no parameters, submitting with default ones.')

    if args.test_modules or args.test_pipeline:
      if args.test_pipeline:
        bp_api.create_analysis(
          control_ids=args.control or [],
          ignore_validation_warnings=args.ignore_warning,
          params=params,
          project_id=args.project,
          sample_ids=args.sample,
          yaml_paths={'pipeline': args.test_pipeline[0]}
        )
      else:
        bp_api.create_analysis(
          control_ids=args.control or [],
          ignore_validation_warnings=args.ignore_warning,
          params=params,
          project_id=args.project,
          sample_ids=args.sample,
          workflow_id=args.workflow,
          yaml_paths={'module': args.test_modules}
        )

  @staticmethod
  def update_analysis(bp_api, analysis_id, keys, vals):
    '''Update analysis'''
    if analysis_id:
      update_info(bp_api, kind='analysis', uid=analysis_id, keys=keys, vals=vals)
    sys.exit('Error: Analysis required.')

  @staticmethod
  def delete_analysis(bp_api, args):
    '''Delete analysis'''
    uids = args.uid
    if not uids:
      sys.exit('Please add one or more uid')

    for uid in uids:
      answer = bp_api.yes_or_no('Are you sure you want to delete {}?'.format(uid))
      if answer:
        bp_api.delete_analysis(uid)

  @staticmethod
  def list_analysis(bp_api, args):
    '''List analyses'''
    bp_api.print_data(data_type='analyses', is_json=args.json, project=args.project)

  @staticmethod
  def reanalyze(bp_api, uid):
    '''Restart analysis'''
    if not uid:
      sys.exit('Please add one or more uid')

    for each_uid in uid:
      bp_api.restart_analysis(each_uid)

  @staticmethod
  def download_log(bp_api, args):
    '''Download analysis log'''
    if not args.uid:
      sys.exit('ERROR: Minimum one analysis uid required.')

    for uid in args.uid:
      info = bp_api.get_analysis(uid)  # check analysis id is valid
      if not info:
        sys.exit('{} is not a valid analysis id!'.format(uid))
      bp_api.get_log(uid, args.outdir)

  @staticmethod
  def download_analysis(bp_api, args):
    '''Download analysis'''
    if not args.uid:
      sys.exit('ERROR: Minimum one analysis uid required.')

    # download a file from an analysis by tags
    for uid in args.uid:
      bp_api.download_analysis(uid, outdir=args.outdir, tagkind=args.tagkind, tags=args.tags)

  
  def verify_yaml(args):
    '''Verify yaml file'''
    if not args.test_pipeline or not args.test_modules:
      eprint('ERROR:at least one Yaml file required.')
      return False
    if args.test_pipeline and len(args.test_pipeline) != 1:
      eprint('Please provide only one pipeline yaml')
      return False
    if args.test_modules:
      yaml_path = args.test_modules
      valid_extensions = ('.yaml', '.yml')
      for each_path in yaml_path:
        if each_path.endswith(valid_extensions):
          return True
      eprint('Please provide yaml file only')
      return False
    yaml_path = args.test_pipeline[0]
    valid_extensions = ('.yaml', '.yml')
    if yaml_path.endswith(valid_extensions):
      return True
    eprint('Please provide yaml file only')
    return False
    
    

  @staticmethod
  def analysis_action_parser(action_parser):
    '''Analysis parser'''
    # get analysis parser
    get_analysis_p = action_parser.add_parser(
      'get',
      help='Get details of an analysis.'
    )
    get_analysis_p = add_common_args(get_analysis_p)
    get_analysis_p = add_uid_parser(get_analysis_p, 'analysis')
    get_analysis_p = add_json_parser(get_analysis_p)

    # create analysis parser
    create_analysis_p = action_parser.add_parser(
      'create',
      help='Create and run an analysis.'
    )
    create_analysis_p = add_common_args(create_analysis_p)
    create_analysis_p.add_argument('--project', help='Project id')
    create_analysis_p.add_argument(
      '--workflow', help='Workflow id'
    )
    create_analysis_p.add_argument(
      '--sample', nargs='+', help='Sample id'
    )
    create_analysis_p.add_argument(
      '--control', nargs='+', help='Control id'
    )
    create_analysis_p.add_argument('--params', nargs='+')
    create_analysis_p.add_argument(
      '--ignore-warning',
      action='store_true',
      default=False,
      help='Ignore validation warnings',
    )
    create_analysis_p.add_argument(
      '--test_modules',
      default=None,
      required=False,
      help='The filepath of module(s) YAML',
      nargs='+'
    )
    create_analysis_p.add_argument(
      '--test_pipeline',
      default=None,
      required=False,
      help='The filepath of Pipeline YAML',
      nargs='+'
    )

    # update an analysis parser
    update_analysis_parser = action_parser.add_parser(
      'update',
      help='Update information associated with an analysis.'
    )
    update_analysis_parser = add_common_args(update_analysis_parser)
    update_analysis_parser = add_single_uid_parser(update_analysis_parser, 'analysis')
    update_analysis_parser.add_argument('--key', action='append')
    update_analysis_parser.add_argument('--val', action='append')

    # delete analysis parser
    delete_analysis_p = action_parser.add_parser(
      'delete',
      help='delete an analysis.'
    )
    delete_analysis_p = add_common_args(delete_analysis_p)
    delete_analysis_p = add_uid_parser(delete_analysis_p, 'analysis')

    # list analysis parser
    list_analyses_p = action_parser.add_parser(
      'list',
      help='List basic info about your analyses.'
    )
    list_analyses_p.add_argument(
      '--project',
      help='List analyses of the project.'
    )
    list_analyses_p = add_common_args(list_analyses_p)
    list_analyses_p = add_json_parser(list_analyses_p)

    # download analysis parser
    download_analysis_p = action_parser.add_parser(
      'download',
      help='Download files for one or more analyses. Can filter by file tags.'
    )
    download_analysis_log_sp = download_analysis_p.add_subparsers(
      help='download log of an analysis.',
      dest='download_type'
    )
    download_analysis_p = add_uid_parser(download_analysis_p, 'analysis')
    download_analysis_p = add_tags_parser(download_analysis_p)
    download_analysis_p = add_outdir_parser(download_analysis_p)
    download_analysis_p = add_common_args(download_analysis_p)

    # reanalyze parser
    reanalyze_p = action_parser.add_parser(
      'reanalyze',
      help='Reanalyze analyses.'
    )
    reanalyze_p = add_common_args(reanalyze_p)
    reanalyze_p = add_uid_parser(reanalyze_p, 'analysis')

    # download analysis log parser
    download_log_p = download_analysis_log_sp.add_parser(
      'log',
      help='Download analysis logs from one or more analyses.'
    )
    download_log_p = add_uid_parser(download_log_p, 'analysis')
    download_log_p = add_outdir_parser(download_log_p)
    download_log_p = add_common_args(download_log_p)

    return action_parser
