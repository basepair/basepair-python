def add_common_args(parser):
  '''Add common args'''
  parser.add_argument('-c', '--config', help='API config info')
  parser.add_argument('--quiet', action='store_true')
  parser.add_argument('--keep-cloud-service-conf', action='store_true')
  parser.add_argument('--use-cache', action='store_true')
  parser.add_argument('--scratch', help='Scratch dir for files')
  parser.add_argument('--verbose', action='store_true')
  parser.set_defaults(scratch='.')
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
    nargs='+',
    default=None,
    help=f'The unique id(s) for {datatype}'
  )
  return parser

def add_pid_parser(parser):
  '''Add pipeline id parser'''
  parser.add_argument(
    '--pipeline',
    nargs='+',
    default=None,
    help='The unique pipeline id'
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
    help=f'(Optional) Override existing {datatype}.'
  )
  return parser