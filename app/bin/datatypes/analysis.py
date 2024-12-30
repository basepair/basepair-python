'''Analysis datatype class'''

# General Import
import sys

# App Import
from basepair.helpers import eprint
from bin.common_parser import add_common_args, add_single_uid_parser, add_uid_parser, add_json_parser, \
  add_tags_parser, add_outdir_parser, valid_uid, validate_analysis_yaml

class Analysis:
  '''Analysis action methods'''

  @staticmethod
  def create_analysis(bp_api, args):
    '''Create and submit an analysis'''
    params = {'node': {}, 'info': {}}
    if args.instance:
      try:
        instance_choices = bp_api.get_instances()
      except KeyError:
        sys.exit('ERROR: Failed to get instance data.')
      if args.instance not in instance_choices:
        sys.exit('ERROR: invalid instance_type available instances - {}'.format(' '.join(instance_choices)))
      params['info']['instance_type'] = args.instance
    if args.custom_pipeline or args.custom_modules:
      validate_analysis_yaml(args.custom_pipeline if args.custom_pipeline else args.custom_modules)
    if args.params:
      for param in args.params:
        try:
          node_id, arg, val = param.split(':')
          if node_id not in params['node']:
            params['node'][node_id] = {}
          params['node'][node_id][arg] = val
        except ValueError:
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
        pipeline_yaml=args.custom_pipeline,
        module_yaml=args.custom_modules
      )

  @staticmethod
  def delete_analysis(bp_api, args):
    '''Delete analysis'''
    uids = args.uid
    all_fail = True
    for uid in uids:
      answer = bp_api.yes_or_no('Are you sure you want to delete {}?'.format(uid))
      if answer:
        all_fail = not bool(bp_api.delete_analysis(uid)) and all_fail
    if all_fail:
      sys.exit('ERROR: Deleting analysis failed.')

  @staticmethod
  def download_analysis(bp_api, args):
    '''Download analysis'''
    # download a file from an analysis by tags
    all_fail = True
    for each_uid in args.uid:
      analysis = bp_api.get_analysis(each_uid)
      all_fail = not (bool(analysis.get('id')) \
        and bool(bp_api.download_analysis(each_uid, analysis=analysis, outdir=args.outdir, tagkind=args.tagkind, tags=args.tags))) \
        and all_fail
    if all_fail:
      sys.exit('ERROR: Downloading analysis failed.')
    eprint('All analysis files have been downloaded successfully.')

  @staticmethod
  def download_log_analysis(bp_api, args):
    '''Download analysis log'''
    all_fail = True
    for uid in args.uid:
      analysis = bp_api.get_analysis(uid)  # check analysis id is valid
      all_fail = not (bool(analysis.get('id')) and bool(bp_api.get_log(uid, args.outdir))) and all_fail
    if all_fail:
      sys.exit('ERROR: Downloading logs failed.')

  @staticmethod
  def get_analysis(bp_api, args):
    '''Get analysis'''
    all_fail = True
    for uid in args.uid:
      all_fail = not bool(bp_api.print_data(data_type='analysis', uid=uid, is_json=args.json)) and all_fail
    if all_fail:
      sys.exit('ERROR: Analyses data not found.')

  @staticmethod
  def list_analysis(bp_api, args):
    '''List analyses'''
    bp_api.print_data(data_type='analyses', is_json=args.json, project=args.project)

  @staticmethod
  def reanalyze_analysis(bp_api, args):
    '''Restart analysis'''
    if args.instance:
      try:
        instance_choices = bp_api.get_instances()
      except KeyError:
        sys.exit('ERROR: Failed to get instance data.')
      if args.instance not in instance_choices:
        sys.exit('ERROR: invalid instance_type available instances - {}'.format(' '.join(instance_choices)))

    all_fail = True
    for each_uid in args.uid:
      all_fail = not bool(bp_api.restart_analysis(each_uid, args.instance)) and all_fail
    if all_fail:
      sys.exit('ERROR: while re-analyze the analysis data.')

  @staticmethod
  def terminate_analysis(bp_api, args):
    '''Terminate analysis'''
    for each_uid in args.uid:
      bp_api.terminate_analysis(each_uid)

  @staticmethod
  def update_analysis(bp_api, args):
    '''Update analysis'''
    data = {}
    if args.key and args.val:
      for key, val in zip(args.key, args.val):
        data[key] = val
    bp_api.update_analysis(args.uid, data)

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
      '--control', nargs='+', help='Control id', type=valid_uid
    )
    create_analysis_p.add_argument(
      '--custom-modules', dest='custom_modules', help='Path to custom module yaml files', nargs='+'
    )
    create_analysis_p.add_argument(
      '--custom-pipeline', dest='custom_pipeline', help='Path to custom pipeline yaml file',
    )
    create_analysis_p.add_argument(
      '--ignore-warning',
      action='store_true',
      default=False,
      help='Ignore validation warnings',
    )
    create_analysis_p.add_argument(
      '--instance', help='instance_type for analysis'
    )
    create_analysis_p.add_argument('--params', nargs='+')
    create_analysis_p.add_argument('--project', help='Project id', type=valid_uid)
    create_analysis_p.add_argument(
      '--pipeline', help='Pipeline id', type=valid_uid
    )
    create_analysis_p.add_argument(
      '--sample', nargs='+', help='Sample id', required=True, type=valid_uid
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
      'download-log',
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
      help='List analyses of a project.',
      required=True,
      type=valid_uid
    )
    list_analyses_p = add_common_args(list_analyses_p)
    list_analyses_p = add_json_parser(list_analyses_p)

    # reanalyze parser
    reanalyze_p = action_parser.add_parser(
      'reanalyze',
      help='Reanalyze analyses.'
    )
    reanalyze_p.add_argument(
      '--instance', help='instance_type for analysis'
    )
    reanalyze_p = add_common_args(reanalyze_p)
    reanalyze_p = add_uid_parser(reanalyze_p, 'analysis')

    # terminate parser
    terminate_p = action_parser.add_parser(
      'terminate',
      help='Terminate analyses.'
    )
    terminate_p = add_common_args(terminate_p)
    terminate_p = add_uid_parser(terminate_p, 'analysis')

    # update an analysis parser
    update_analysis_parser = action_parser.add_parser(
      'update',
      help='Update information associated with an analysis.'
    )
    update_analysis_parser.add_argument('--key', action='append', required=True)
    update_analysis_parser.add_argument('--val', action='append', required=True)
    update_analysis_parser = add_common_args(update_analysis_parser)
    update_analysis_parser = add_single_uid_parser(update_analysis_parser, 'analysis')

    return action_parser
