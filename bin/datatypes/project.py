'''Project dataype class'''

import json
import sys
# App imports
from bin.common_parser import add_common_args, add_payload_args, add_json_parser

class Project:
  '''Project action methods'''

  @staticmethod
  def create_project(bp_api, args):
    '''Create project'''
    data = {'name': args.name}
    bp_api.create_project(data=data)

  @staticmethod
  def get_project(bp_api, args):
    '''Create project'''
    bp_api.get_project(name=args.name)

  @staticmethod
  def list_project(bp_api, args):
    '''List pipelines'''
    bp_api.print_data(data_type='projects', is_json=args.json)

  @staticmethod
  def update_project(bp_api, args):
    '''Update project'''
    if args.project:
      data = {}
      if args.name:
        data = {'name': args.name}

      params = {}
      if args.emails and args.perm:
        params = {
          'params': json.dumps({
            'permission_data': {
              'emails': args.emails,
              'perm': args.perm,
            }
          })
        }

      if not data and not params:
        sys.exit('WARNING: No data to update.')

      for project_id in args.project:
        res = bp_api.update_project(project_id, data=data, params=params)

        if res.get('error'):
          sys.exit(f"error: {res.get('msg')}")
      return
    sys.exit('ERROR: Minimum one project required.')

  @staticmethod
  def project_action_parser(action_parser):
    '''project parser'''

    # create project parser
    create_project_p = action_parser.add_parser(
      'create',
      help='Add a project to your account on Basepair.'
    )
    create_project_p.add_argument('--name')
    create_project_p = add_common_args(create_project_p)
    create_project_p = add_payload_args(create_project_p)

    # list project parser
    list_project_p = action_parser.add_parser(
      'list',
      help='Add a project to your account on Basepair.'
    )
    list_project_p = add_common_args(list_project_p)
    list_project_p = add_json_parser(list_project_p)

    # update project parser
    update_project_parser = action_parser.add_parser(
      'update',
      help='Update information associated with a project.'
    )
    update_project_parser = add_common_args(update_project_parser)
    update_project_parser.add_argument('--emails', default=[], nargs='+')
    update_project_parser.add_argument('--name')
    update_project_parser.add_argument(
      '--perm', choices=['admin', 'edit', 'view'], default='view')
    update_project_parser.add_argument(
      '--project', nargs='+', help='project id', required=True
    )

    return action_parser
