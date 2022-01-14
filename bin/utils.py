import sys





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