'''Pipeline datatype class'''
import json
# General Import
import sys

# App imports
from bin.common_parser import add_common_args, add_uid_parser, add_json_parser, add_yaml_parser, add_force_parser, \
  validate_create_yaml, validate_update_yaml, valid_email, add_single_uid_parser


class Pipeline:
  '''Pipeline action methods'''

  @staticmethod
  def create_pipeline(bp_api, args):
    '''Create pipeline'''
    valid = validate_create_yaml(args)
    if valid:
      for each_yaml in args.file:
        bp_api.create_pipeline({'yamlpath': each_yaml, 'force': args.force})

  @staticmethod
  def delete_pipeline(bp_api, args):
    '''Delete pipeline'''
    all_fail = True
    for uid in args.uid:
      answer = bp_api.yes_or_no('Are you sure you want to delete {}?'.format(uid))
      if answer:
        all_fail = not bool(bp_api.delete_pipeline(uid)) and all_fail
    if all_fail:
      sys.exit('ERROR: Deleting Pipeling failed.')

  @staticmethod
  def get_pipeline(bp_api, args):
    '''Get pipeline'''
    all_fail = True
    for uid in args.uid:
      all_fail = not bool(bp_api.print_data(data_type='pipeline', uid=uid, is_json=args.json)) and all_fail
    if all_fail:
      sys.exit('ERROR: Pipeline data not found.')

  @staticmethod
  def list_pipeline(bp_api, args):
    '''List pipelines'''
    bp_api.print_data(data_type='pipelines', is_json=args.json)

  @staticmethod
  def update_pipeline(bp_api, args):
    '''Update pipeline'''

    if (args.emails and not args.perm) or (args.perm and not args.emails):
      sys.exit('ERROR: Please provide permission and emails to update.')

    if args.emails and args.perm:
      params = {
        'params': json.dumps({
          'permission_data': {
            'emails': args.emails,
            'perm': args.perm,
          }
        })
      }
      bp_api.update_pipeline(params=params, pipeline_id=args.uid)
    else:
      if validate_update_yaml(args):
        bp_api.update_pipeline(data={'yamlpath': args.file[0]})

  @staticmethod
  def pipeline_action_parser(action_parser):
    '''Pipeline parser'''

    # create pipeline parser
    create_pipeline_p = action_parser.add_parser(
      'create',
      help='Create pipeline from yaml.'
    )
    create_pipeline_p = add_common_args(create_pipeline_p)
    create_pipeline_p = add_yaml_parser(create_pipeline_p)
    create_pipeline_p = add_force_parser(create_pipeline_p, 'pipeline')

    # delete pipeline parser
    delete_pipeline_p = action_parser.add_parser(
      'delete',
      help='delete a pipeline.'
    )
    delete_pipeline_p = add_common_args(delete_pipeline_p)
    delete_pipeline_p = add_uid_parser(delete_pipeline_p, 'pipeline')

    # get pipeline parser
    get_pipeline_p = action_parser.add_parser(
      'get',
      help='Get details of a pipeline.'
    )
    get_pipeline_p = add_common_args(get_pipeline_p)
    get_pipeline_p = add_uid_parser(get_pipeline_p, 'pipeline')
    get_pipeline_p = add_json_parser(get_pipeline_p)

    # list pipeline parser
    list_pipelines_p = action_parser.add_parser(
      'list',
      help='List available pipelines.'
    )
    list_pipelines_p = add_common_args(list_pipelines_p)
    list_pipelines_p = add_json_parser(list_pipelines_p)

    # update pipeline parser
    update_pipeline_parser = action_parser.add_parser(
      'update',
      help='Update information associated with a pipeline.'
    )
    update_pipeline_parser = add_common_args(update_pipeline_parser)
    update_pipeline_parser = add_yaml_parser(update_pipeline_parser)
    update_pipeline_parser = add_force_parser(update_pipeline_parser, 'pipeline')
    update_pipeline_parser.add_argument('--emails', default=[], nargs='+', type=valid_email)
    update_pipeline_parser.add_argument('--perm', choices=['admin', 'edit', 'view'])
    update_project_parser = add_single_uid_parser(update_pipeline_parser, 'pipeline')

    return action_parser
