import json

# App imports
from basepair.helpers import eprint

from bin.utils import check_yaml
from bin.common_parser import add_common_args, add_payload_args, add_uid_parser, add_json_parser


class Project:
    
    '''Project action methods'''

    def create_project(bp, args):
        '''Create project'''
        data = {'name': args.name}
        bp.create_project(data=data)

    def update_project(bp, args):
        '''Update project'''
        if not args.project:
            eprint('ERROR: Minimum one project required.')
            return

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
            eprint('WARNING: No data to update.')
            return

        for project_id in args.project:
            res = bp.update_project(project_id, data=data, params=params)

            if res.get('error'):
                eprint('error: {}'.format(res.get('msg')))

    def list_project(bp, args):
      '''List pipelines'''
      bp.print_data(data_type='projects', is_json=args.json)


    def project_action_parser(action_parser):
        # list project parser
        list_project_p = action_parser.add_parser(
          'list',
          help='Add a project to your account on Basepair.'
        )
        list_project_p = add_common_args(list_project_p)
        list_project_p = add_json_parser(list_project_p)

        # create project parser
        create_project_p = action_parser.add_parser(
          'create',
          help='Add a project to your account on Basepair.'
        )
        create_project_p = add_common_args(create_project_p)
        create_project_p.add_argument('--name')
        create_project_p = add_payload_args(create_project_p)

        # update project parser
        update_project_parser = action_parser.add_parser(
          'update',
          help='Update information associated with a project.'
        )
        update_project_parser = add_common_args(update_project_parser)
        update_project_parser.add_argument(
          '--project', nargs='+', help='project id', required=True
        )
        update_project_parser.add_argument('--emails', default=[], nargs='+')
        update_project_parser.add_argument('--perm', choices=['admin', 'edit', 'view'], default='view')
        update_project_parser.add_argument('--name')

        return action_parser
