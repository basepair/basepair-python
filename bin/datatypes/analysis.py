'''Analysis datatype class'''
import sys
# App Import
from basepair.helpers import eprint
from bin.common_parser import add_common_args, add_single_uid_parser, add_uid_parser, add_json_parser, add_tags_parser, add_outdir_parser

class Analysis:
  '''Analysis action methods'''

  @staticmethod
  def create_analysis(bp_api, args):
    '''Create and submit an analysis'''
    params = {'node': {}}

    if not args.pipeline:
      sys.exit('ERROR: Pipeline uid required.')

    if not args.sample:
      sys.exit('ERROR: Sample uid required.')

    if args.params:
      for param in args.params:
        try:
          node_id, arg, val = param.split(':')
          if node_id not in params['node']:
            params['node'][node_id] = {}
          params['node'][node_id][arg] = val
        except:
          sys.exit('ERROR: Missing : in params values.')
    else:
      eprint('You specified no parameters, submitting with default ones.')
    return bp_api.create_analysis(
        control_ids=args.control or [],
        ignore_validation_warnings=args.ignore_warning,
        params=params,
        project_id=args.project,
        sample_ids=args.sample,
        workflow_id=args.pipeline,
        instance=args.instance
      )

  @staticmethod
  def delete_analysis(bp_api, args):
    '''Delete analysis'''
    uids = args.uid
    if uids:
      for uid in uids:
        answer = bp_api.yes_or_no('Are you sure you want to delete {}?'.format(uid))
        if answer:
          bp_api.delete_analysis(uid)
      return
    sys.exit('ERROR: At least one uid required.')

  @staticmethod
  def download_analysis(bp_api, args):
    '''Download analysis'''
    if args.uid:
      # download a file from an analysis by tags
      for uid in args.uid:
        bp_api.download_analysis(uid, outdir=args.outdir, tagkind=args.tagkind, tags=args.tags)
      sys.exit('All analysis files have been downloaded succesfully.')
    sys.exit('ERROR: At least one uid required.')

  @staticmethod
  def download_log_analysis(bp_api, args):
    '''Download analysis log'''
    print('logger')
    if args.uid:
      for uid in args.uid:
        info = bp_api.get_analysis(uid)  # check analysis id is valid
        if info.get('id'):
          bp_api.get_log(uid, args.outdir)
      return
    sys.exit('ERROR: At least one uid required.')

  @staticmethod
  def get_analysis(bp_api, args):
    '''Get analysis'''
    uids = args.uid
    is_json = args.json
    if uids:
      for uid in uids:
        bp_api.print_data(data_type='analysis', uid=uid, is_json=is_json)
      return
    sys.exit('ERROR: At least one uid required.')

  @staticmethod
  def list_analysis(bp_api, args):
    '''List analyses'''
    bp_api.print_data(data_type='analyses', is_json=args.json, project=args.project)

  @staticmethod
  def reanalyze_analysis(bp_api, args):
    '''Restart analysis'''
    if args.uid:
      for each_uid in args.uid:
        bp_api.restart_analysis(each_uid)
      return
    sys.exit('ERROR: At least one uid required.')

  @staticmethod
  def update_analysis(bp_api, analysis_id, keys, vals):
    '''Update analysis'''
    try:
      if analysis_id:
        data = {}
        if keys and vals:
          for key, val in zip(keys, vals):
            data[key] = val
        res = bp_api.update_analysis(analysis_id, data)
        if res.get('error'):
          sys.exit('ERROR: {}'.format(res.get('msg')))
        return
      sys.exit('ERROR: At least one uid required.')
    except:
      sys.exit('ERROR: Something went wrong while updating analysis.')

  @staticmethod
  def analysis_action_parser(action_parser):
    '''Analysis parser'''

    # create analysis parser
    create_analysis_p = action_parser.add_parser(
      'create',
      help='Create and run an analysis.'
    )
    create_analysis_p = add_common_args(create_analysis_p)
    create_analysis_p.add_argument(
      '--control', nargs='+', help='Control id'
    )
    create_analysis_p.add_argument(
      '--ignore-warning',
      action='store_true',
      default=False,
      help='Ignore validation warnings',
    )
    create_analysis_p.add_argument('--params', nargs='+')
    create_analysis_p.add_argument('--project', help='Project id')
    create_analysis_p.add_argument(
      '--sample', nargs='+', help='Sample id'
    )
    create_analysis_p.add_argument(
      '--pipeline', help='Pipeline id'
    )
    create_analysis_p.add_argument(
      '--instance', help='instance'
    )

    # delete analysis parser
    delete_analysis_p = action_parser.add_parser(
      'delete',
      help='delete an analysis.'
    )
    delete_analysis_p = add_common_args(delete_analysis_p)
    delete_analysis_p = add_uid_parser(delete_analysis_p, 'analysis')

    # download analysis parser
    download_analysis_p = action_parser.add_parser(
      'download',
      help='Download files for one or more analyses. Can filter by file tags.'
    )
    download_analysis_p = add_uid_parser(download_analysis_p, 'analysis')
    download_analysis_p = add_tags_parser(download_analysis_p)
    download_analysis_p = add_outdir_parser(download_analysis_p)
    download_analysis_p = add_common_args(download_analysis_p)

    # download analysis log parser
    download_log_p = action_parser.add_parser(
      'download_log',
      help='Download analysis logs for one or more analyses.'
    )
    download_log_p = add_uid_parser(download_log_p, 'analysis')
    download_log_p = add_outdir_parser(download_log_p)
    download_log_p = add_common_args(download_log_p)

    # get analysis parser
    get_analysis_p = action_parser.add_parser(
      'get',
      help='Get details of an analysis.'
    )
    get_analysis_p = add_common_args(get_analysis_p)
    get_analysis_p = add_uid_parser(get_analysis_p, 'analysis')
    get_analysis_p = add_json_parser(get_analysis_p)

    # list analysis parser
    list_analyses_p = action_parser.add_parser(
      'list',
      help='List basic info about your analyses.'
    )
    list_analyses_p.add_argument(
      '--project',
      help='List analyses of the project.',
      required=True
    )
    list_analyses_p = add_common_args(list_analyses_p)
    list_analyses_p = add_json_parser(list_analyses_p)

    # reanalyze parser
    reanalyze_p = action_parser.add_parser(
      'reanalyze',
      help='Reanalyze analyses.'
    )
    reanalyze_p = add_common_args(reanalyze_p)
    reanalyze_p = add_uid_parser(reanalyze_p, 'analysis')

    # update an analysis parser
    update_analysis_parser = action_parser.add_parser(
      'update',
      help='Update information associated with an analysis.'
    )
    update_analysis_parser.add_argument('--key', action='append')
    update_analysis_parser.add_argument('--val', action='append')
    update_analysis_parser = add_common_args(update_analysis_parser)
    update_analysis_parser = add_single_uid_parser(update_analysis_parser, 'analysis')

    return action_parser
