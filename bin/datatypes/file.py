import json

# App imports
from basepair.helpers import eprint

from bin.utils import check_yaml
from bin.common_parser import add_uid_parser, add_common_args, add_outdir_parser


class File:
    
    '''File action methods'''

    def download_file(bp, args):
        '''Download file by uid'''
        if not args.uid:
            eprint('ERROR: Minimum one file uid required.')
            return

        for uid in args.uid:
            file_i = bp.get_file(uid)
            bp.download_file(file_i['path'], dirname=args.outdir)

    def file_action_parser(action_parser):
        # download file parser
        download_file_p = action_parser.add_parser(
          'download',
          help='Download one or more files by uid.'
        )
        download_file_p = add_uid_parser(download_file_p, 'file')
        download_file_p = add_outdir_parser(download_file_p)
        download_file_p = add_common_args(download_file_p)

        return action_parser
