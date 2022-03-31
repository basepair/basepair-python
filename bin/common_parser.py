'''Common parser used in datatypes parsing'''
import argparse
import sys, os
import re
# App imports
from basepair.helpers import eprint

def validate_conf(args):
  '''Helper to validate the proper configuration argument is being set'''
  if args.config:
    return eprint('Using config file', args.config)
  if 'BP_CONFIG_FILE' in os.environ:
    return eprint(f"Using config file {os.environ['BP_CONFIG_FILE']}")
  return sys.exit('ERROR: Please either use the -c or --config param or set the environment variable BP_CONFIG_FILE!')

def is_valid_yaml_arg(args):
  '''Checks yaml file'''
  if not args.file:
    sys.exit('ERROR: Yaml file required.')
  if len(args.file) != 1:
    sys.exit('ERROR: Please provide only one yaml')
  yaml_path = args.file[0]
  valid_extensions = ('.yaml', '.yml')
  if yaml_path.endswith(valid_extensions):
    return True
  sys.exit('Please provide yaml file only')

def add_common_args(parser):
  '''Add common args'''
  parser.add_argument('-c', '--config', help='API config info')
  parser.add_argument('--quiet', action='store_true')
  parser.add_argument('--keep-cloud-service-conf', action='store_true')
  parser.add_argument('--use-cache', action='store_true')
  parser.add_argument('--scratch', default='.', help='Scratch dir for files')
  parser.add_argument('--verbose', action='store_true')
  return parser

def add_payload_args(parser):
  '''Add payload args'''
  parser.add_argument(
    '--payload-username',
    help='Replace payload api key. Must also specify --payload-api-key'
  )
  parser.add_argument(
    '--payload-api-key',
    help='Replace payload api key. Must also specify --payload-username'
  )
  return parser

def add_uid_parser(parser,datatype):
  '''Add uid parser'''
  parser.add_argument(
    '-u',
    '--uid',
    default=None,
    help='The unique id(s) for {}'.format(datatype),
    nargs='+',
    required=True,
    type=valid_uid
  )
  return parser

def add_single_uid_parser(parser,datatype):
  '''Add single uid parser'''
  parser.add_argument(
    '-u',
    '--uid',
    help='The unique id for {}'.format(datatype),
    required=True,
    type=valid_uid
  )
  return parser

def add_pid_parser(parser):
  '''Add pipeline id parser'''
  parser.add_argument(
    '--pipeline',
    help='A unique pipeline id',
    required=True,
    type=valid_uid
  )
  return parser

def add_json_parser(parser):
  '''Add json parser'''
  parser.add_argument(
    '--json',
    action='store_true',
    help='(Optional) Print the data in JSON format (this shows all data associated with each item).'
  )
  return parser

def add_outdir_parser(parser):
  '''Add outdir parser'''
  parser.add_argument(
    '-o',
    '--outdir',
    required=False,
    default='.',
    help='Base directory to save files to (default \'.\').'
  )
  return parser

def add_tags_parser(parser):
  '''Add tags parser'''
  parser.add_argument(
    '--tags',
    nargs='+',
    action='append',
    default=None
  )
  parser.add_argument(
    '--tagkind',
    choices=['diff', 'exact', 'subset'],
    default='exact',
    help='''
             Tag filtering strategy. Options:\n
             (1) exact (default): only get files with exactly these tags.
             (2) diff: exclude files with this tag.
             (3) subset: any files with one or more of these tags.
             '''
  )
  return parser

def add_yaml_parser(parser):
  '''Add yaml file parser'''
  parser.add_argument(
    '--file',
    default=None,
    required=True,
    help='The filepath of YAML',
    nargs='+'
  )
  return parser

def add_force_parser(parser, datatype):
  '''Add force parser'''
  parser.add_argument(
    '--force',
    action='store_true',
    help='(Optional) Override existing {}.'.format(datatype)
  )
  return parser

def valid_uid(value):
  if value.isdigit() and int(value) > 0:
    return value
  raise argparse.ArgumentTypeError('ERROR: uid must be a positive integer'.format(value))

def valid_email(value):
  pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
  if not pattern.match(value):
    raise argparse.ArgumentTypeError('ERROR: Invalid email format.'.format(value))
  return value