'''Sample webapp api wrapper'''

# Lib imports
import json
import os
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class Sample(Abstract):
  '''Webapp Sample class'''
  def __init__(self, cfg):
    super(Sample, self).__init__(cfg)
    self.endpoint += 'samples/'

  def by_name(self, name, project_id, cache=False, verify=True): # pylint: disable=dangerous-default-value
    '''Get detail of an resource'''
    if cache:
      filename = os.path.expanduser(cache)
      if os.path.exists(filename) and os.path.getsize(filename):
        return json.loads(open(filename, 'r').read().strip())

    try:
      response = requests.get(
        '{}/by_name'.format(self.endpoint),
        params={'name': name, 'project_id': project_id, **self.payload},
        verify=verify,
      )
      parsed = self._parse_response(response)

      # save in cache if required
      if cache and parsed and not parsed.get('error'):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
          os.makedirs(directory)
        with open(filename, 'w') as handle:
          handle.write(json.dumps(parsed, indent=2))
      return parsed
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}
