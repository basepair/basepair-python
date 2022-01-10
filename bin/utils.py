import sys
# App imports
from basepair.helpers import eprint


def check_yaml(args):
  '''Checks yaml file'''
  if not args.file:
    eprint('ERROR: Yaml file required.')
    return False
  if len(args.file) != 1:
    eprint('Please provide only one yaml')
    return False
  yaml_path = args.file[0]
  valid_extensions = ('.yaml', '.yml')
  if yaml_path.endswith(valid_extensions):
    return True
  eprint('Please provide yaml file only')
  return False

def update_info(bp, kind=None, uid=None, keys=None, vals=None, data={}):
  '''Update object info'''
  if keys and vals:
    for key, val in zip(keys, vals):
      if kind == 'sample' and key in ['adapter', 'amplicon', 'barcode', 'regions', 'stranded']:
        data['info'] = data.get('info', {})
        data['info'][key] = val  # set sample info field
      else:
        data[key] = val

  method_name = f'update_{kind}'
  method = getattr(bp, method_name, None)
  if callable(method):
    res = method(uid, data)
  res = {'error': True, 'msg': f'Update {kind} not supported.'}
  if res.get('error'):
    sys.exit(f"ERROR: {res.get('msg')}")