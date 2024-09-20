'''Common parser used in datatypes parsing'''
import argparse
import os
import re
import sys

# App imports
from basepair.helpers import eprint

def add_common_args(parser):
  '''Add common args'''
  parser.add_argument('-c', '--config', help='Path to API config file')
  parser.add_argument('--quiet', action='store_true')
  parser.add_argument('--cache-cloud-credential', dest='keep_cloud_service_conf', action='store_true')
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

def add_force_parser(parser, datatype):
  '''Add force parser'''
  parser.add_argument(
    '--force',
    action='store_true',
    help='(Optional) Override existing {}.'.format(datatype)
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

def add_uid_parser(parser, datatype):
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

def add_yaml_parser(parser):
  '''Add yaml file parser'''
  parser.add_argument(
    '--file',
    default=None,
    required=False,
    help='The filepath of YAML',
    nargs='+'
  )
  return parser

def valid_uid(value):
  '''Validates the uid for positive integer'''
  if value.isdigit() and int(value) > 0:
    return value
  raise argparse.ArgumentTypeError('ERROR: uid must be a positive integer')

def valid_email(value):
  '''Validates the email'''
  pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
  if pattern.match(value):
    return value
  raise argparse.ArgumentTypeError('ERROR: Invalid email format.')

valid_sample_extensions = ('.ab1', '.bai', '.bam', '.crai', '.csfasta', '.csv', '.fasta', '.fastq', '.fq', '.gvcf', '.qual', '.vcf', '.sam', '.sra', '.txt', '.bz', '.bz2', '.gz', '.zip')

def validate_sample_file(files):
  '''Validates sample file type'''
  for file in files:
    if not file.endswith(valid_sample_extensions):
      sys.exit('ERROR: Please provide valid sample file. Available File types - {}'.format(' '.join(valid_sample_extensions)))
  return True

def validate_conf(args):
  '''Helper to validate the proper configuration argument is being set'''
  if args.config:
    return eprint('Using config file', args.config)
  if 'BP_CONFIG_FILE' in os.environ:
    return eprint('Using config file {}'.format(os.environ['BP_CONFIG_FILE']))
  return sys.exit('ERROR: Please either use the -c or --config param or set the environment variable BP_CONFIG_FILE!')

def validate_analysis_yaml(yaml_argument):
  '''Checks yaml file'''
  if not isinstance(yaml_argument, list):
    yaml_argument = [yaml_argument]
  for each_yaml in yaml_argument:
    valid_extensions = ('.yaml', '.yml')
    if not each_yaml.endswith(valid_extensions):
      sys.exit('ERROR: Please provide yaml file with extension .yaml, .yml ')
    elif not os.path.isfile(each_yaml):
      sys.exit('ERROR: File does not exist at {}.'.format(each_yaml))
  return True

def validate_update_yaml(args):
  '''Validates yaml file'''
  if not args.file:
    sys.exit('ERROR: Yaml file required.')
  if len(args.file) != 1:
    sys.exit('ERROR: Please provide only one yaml')
  yaml_path = args.file[0]
  valid_extensions = ('.yaml', '.yml')
  if not yaml_path.endswith(valid_extensions):
    sys.exit('ERROR: Please provide yaml file with extension .yaml, .yml ')
  elif not os.path.isfile(yaml_path):
    sys.exit('ERROR: File does not exist at {}.'.format(yaml_path))
  return True

def validate_create_yaml(args):
  '''Validates yaml file'''
  if not args.file:
    sys.exit('ERROR: Yaml file required.')
  for i in range(0, len(args.file)):
    yaml_path = args.file[i]
    valid_extensions = ('.yaml', '.yml')
    if not yaml_path.endswith(valid_extensions):
      sys.exit('ERROR: Please provide yaml file with extension .yaml, .yml ')
    elif not os.path.isfile(yaml_path):
      sys.exit('ERROR: File does not exist at {}.'.format(yaml_path))
  return True
