'''User webapp api wrapper'''

# General imports
import json
import os

# Lib imports
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class User(Abstract):
  '''Webapp User class'''
  def __init__(self, cfg):
    super().__init__(cfg)
    self.endpoint += 'users/'

  def get_configuration(self, cache=False, verify=True):
    '''Get host configuration for user'''
    if cache:
      filename = os.path.expanduser(cache)
      if os.path.exists(filename) and os.path.getsize(filename):
        return json.loads(open(filename, 'r').read().strip())

    params = {'origin': 'cli'}
    params.update(self.payload)
    try:
      response = requests.get(
        '{}get_configuration'.format(self.endpoint),
        params=params,
        verify=verify,
      )
      parsed = self._parse_response(response)

      # save in cache if required
      if cache and parsed and not parsed.get('error'):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
          os.makedirs(directory)
        eprint('Saving configuration into:', filename)
        with open(filename, 'w') as handle:
          handle.write(json.dumps(parsed, indent=2))
      return parsed
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return { 'error': True, 'msg': error}
