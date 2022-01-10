'''Module datatype class'''
# App imports
from basepair.helpers import eprint
from bin.utils import check_yaml
from bin.common_parser import add_common_args, add_uid_parser, add_json_parser, add_yaml_parser, add_pid_parser, add_force_parser


class Module:

  '''Module action methods'''

  @staticmethod
  def get_module(bp_api, args):
    '''Get module'''
    uids = args.uid
    is_json = args.json
    if not uids:
      eprint('At least one uid required.')
      return
    for uid in uids:
      bp_api.print_data(data_type='module', uid=uid, is_json=is_json)

  @staticmethod
  def create_module(bp_api, args):
    '''Create module'''
    valid = check_yaml(args)
    if valid:
      bp_api.create_module({'yamlpath': args.file[0], 'force': args.force})
      return
    return

  @staticmethod
  def update_module(bp_api, args):
    '''Update module'''
    valid = check_yaml(args)
    if valid:
      bp_api.update_module({'yamlpath': args.file[0]})
      return
    return

  @staticmethod
  def delete_module(bp_api, args):
    '''Delete Module'''
    uids = args.uid
    if not uids:
      eprint('Please add one or more uid')
      return

    for uid in uids:
      answer = bp_api.yes_or_no('Are you sure you want to delete {}?'.format(uid))
      if answer:
        bp_api.delete_module(uid)

  @staticmethod
  def list_module(bp_api, args):
    '''List Modules'''
    uids = args.pipeline
    is_json = args.json
    if not uids:
      eprint('Please provide only one pipeline uid.')
      return

    if len(uids) > 1:
      eprint('Please provide only one pipeline uid.')
      return

    for uid in uids:
      bp_api.print_data(data_type='pipeline_modules', uid=uid, is_json=is_json)

  @staticmethod
  def module_action_parser(action_parser):
    '''Module parser'''
    #get module parser'''
    get_module_p = action_parser.add_parser(
        'get',
        help='Get details of a module'
    )
    get_module_p = add_common_args(get_module_p)
    get_module_p = add_uid_parser(get_module_p, 'module')
    get_module_p = add_json_parser(get_module_p)

    # create module parser
    create_module_p = action_parser.add_parser(
        'create',
        help='Create module from yaml.'
    )
    create_module_p = add_common_args(create_module_p)
    create_module_p = add_yaml_parser(create_module_p)
    create_module_p = add_force_parser(create_module_p, 'module')

    # update module parser
    update_module_parser = action_parser.add_parser(
        'update',
        help='Update information associated with a module.'
    )
    update_module_parser = add_common_args(update_module_parser)
    update_module_parser = add_yaml_parser(update_module_parser)

    # delete module parser
    delete_module_p = action_parser.add_parser(
        'delete',
        help='delete a module.'
    )
    delete_module_p = add_common_args(delete_module_p)
    delete_module_p = add_uid_parser(delete_module_p, 'module')

    # list module parser
    list_modules_p = action_parser.add_parser(
        'list',
        help='List available modules of a pipeline.'
    )
    list_modules_p = add_common_args(list_modules_p)
    list_modules_p = add_pid_parser(list_modules_p)
    list_modules_p = add_json_parser(list_modules_p)

    return action_parser
