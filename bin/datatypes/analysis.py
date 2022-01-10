# App imports
from basepair.helpers import eprint

from bin.utils import check_yaml, update_info
from bin.common_parser import add_common_args, add_single_uid_parser, add_uid_parser, add_json_parser, add_tags_parser, add_outdir_parser

class Analysis:
    
    '''Analysis action methods'''

    def get_analysis(bp, args):
      '''Get analysis'''
      uids=args.uid
      is_json=args.json
      if not uids:
        eprint('At least one uid required.')
        return
      for uid in uids:
        bp.print_data(data_type='analysis', uid=uid, is_json=is_json)

    def create_analysis(bp, args):
        '''Create and submit an analysis'''
        params = {'node': {}}

        if not args.workflow:
            eprint('ERROR: Workflow required.')
            return

        if not args.sample:
            eprint('ERROR: Minimum one sample required.')
            return

        if args.params:
            for param in args.params:
                node_id, arg, val = param.split(':')
                if node_id not in params['node']:
                    params['node'][node_id] = {}
                params['node'][node_id][arg] = val
        else:
            eprint('You specified no parameters, submitting with default ones...')

        bp.create_analysis(
            control_ids=args.control or [],
            ignore_validation_warnings=args.ignore_warning,
            params=params,
            project_id=args.project,
            sample_ids=args.sample,
            workflow_id=args.workflow,
        )

    def update_analysis(bp, analysis_id, keys, vals):
        '''Update analysis'''
        if not analysis_id:
            eprint('Error: Analysis required.')
            return
        update_info(bp, kind='analysis', uid=analysis_id, keys=keys, vals=vals)

    def delete_analysis(bp, args):
        '''Delete analysis'''
        uids = args.uid
        if not uids:
            eprint('Please add one or more uid')
            return

        for uid in uids:
            answer = bp.yes_or_no('Are you sure you want to delete {}?'.format(uid))
            if answer:
                bp.delete_analysis(uid)

    def list_analysis(bp, args):
        '''List analyses'''
        bp.print_data(data_type='analyses', is_json=args.json, project=args.project)

    def reanalyze(bp, uid):
        '''Restart analysis'''
        if not uid:
            eprint('Please add one or more uid')
            return

        for uid in uid:
            bp.restart_analysis(uid)

    def download_log(bp, args):
        '''Download analysis log'''
        if not args.uid:
            eprint('ERROR: Minimum one analysis uid required.')
            return

        for uid in args.uid:
            info, res = bp.get_analysis(uid)  # check analysis id is valid
            if info is None:
                eprint('{} is not a valid analysis id!'.format(uid))
                continue

            if args.outdir:
                bp.get_log(uid, args.outdir)
            else:
                bp.get_log(uid)

    def download_analysis(bp, args):
        '''Download analysis'''
        if not args.uid:
            eprint('ERROR: Minimum one analysis uid required.')
            return

        # download a file from an analysis by tags
        for uid in args.uid:
            bp.download_analysis(uid, outdir=args.outdir, tagkind=args.tagkind, tags=args.tags)


    def analysis_action_parser(action_parser):
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
