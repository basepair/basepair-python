'''File datatype class'''

# General Import
import sys

# App imports
from bin.common_parser import add_uid_parser, add_common_args, add_outdir_parser

class File:
  '''File action methods'''

  @staticmethod
  def download_file(bp_api, args):
    '''Download file by uid'''
    all_fail = True
    for uid in args.uid:
      file_i = bp_api.get_file(uid)
      all_fail = not (bool(file_i.get('id')) \
        and bool(bp_api.download_file(file_i['path'], uid=uid, dirname=args.outdir, file_type='files'))) \
        and all_fail
    if all_fail:
      sys.exit('ERROR: File downloading failed.')

  @staticmethod
  def file_action_parser(action_parser):
    '''File datatype action parser'''
    download_file_p = action_parser.add_parser(
      'download',
      help='Download one or more files by uid.'
    )
    download_file_p = add_uid_parser(download_file_p, 'file')
    download_file_p = add_outdir_parser(download_file_p)
    download_file_p = add_common_args(download_file_p)

    return action_parser
