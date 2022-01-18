'''Pipeline datatype class'''
import sys
# App imports
from bin.common_parser import add_common_args, add_uid_parser, add_json_parser, add_yaml_parser, add_force_parser, is_valid_yaml_arg

class Pipeline:
  '''Pipeline action methods'''

  @staticmethod
  def get_pipeline(bp_api, args):
    '''Get pipeline'''
    uids = args.uid
    is_json = args.json
    if uids:
      for uid in uids:
        bp_api.print_data(data_type='pipeline', uid=uid, is_json=is_json)
    sys.exit('At least one uid required.')

  @staticmethod
  def create_pipeline(bp_api, args):
    '''Create pipeline'''
    valid = is_valid_yaml_arg(args)
    if valid:
      bp_api.create_pipeline({'yamlpath': args.file[0], 'force': args.force})

  @staticmethod
  def update_pipeline(bp_api, args):
    '''Update pipeline'''
    valid = is_valid_yaml_arg(args)
    if valid:
      bp_api.update_pipeline({'yamlpath': args.file[0]})

  @staticmethod
  def delete_pipeline(bp_api, args):
    '''Delete pipeline'''
    uids = args.uid
    if uids:
      for uid in uids:
        answer = bp_api.yes_or_no('Are you sure you want to delete {}?'.format(uid))
        if answer:
          bp_api.delete_pipeline(uid)
    sys.exit('Please add one or more uid')

  @staticmethod
  def list_pipeline(bp_api, args):
    '''List pipelines'''
    bp_api.print_data(data_type='pipelines', is_json=args.json)

  @staticmethod
  def pipeline_action_parser(action_parser):
    '''Pipeline parser'''
    #get pipeline parser
    get_pipeline_p = action_parser.add_parser(
      'get',
      help='Get details of a pipeline.'
    )
    get_pipeline_p = add_common_args(get_pipeline_p)
    get_pipeline_p = add_uid_parser(get_pipeline_p, 'pipeline')
    get_pipeline_p = add_json_parser(get_pipeline_p)

    # create pipeline parser
    create_pipeline_p = action_parser.add_parser(
      'create',
      help='Create pipeline from yaml.'
    )
    create_pipeline_p = add_common_args(create_pipeline_p)
    create_pipeline_p = add_yaml_parser(create_pipeline_p)
    create_pipeline_p = add_force_parser(create_pipeline_p, 'pipeline')

    # update pipeline parser
    update_pipeline_parser = action_parser.add_parser(
      'udpate',
      help='Update information associated with a pipeline.'
    )
    update_pipeline_parser = add_common_args(update_pipeline_parser)
    update_pipeline_parser = add_yaml_parser(update_pipeline_parser)

    # delete pipeline parser
    delete_pipeline_p = action_parser.add_parser(
      'delete',
      help='delete a pipeline.'
    )
    delete_pipeline_p = add_common_args(delete_pipeline_p)
    delete_pipeline_p = add_uid_parser(delete_pipeline_p, 'pipeline')

    # list pipeline parser
    list_pipelines_p = action_parser.add_parser(
      'list',
      help='List available pipelines.'
    )
    list_pipelines_p = add_common_args(list_pipelines_p)
    list_pipelines_p = add_json_parser(list_pipelines_p)

    return action_parser
