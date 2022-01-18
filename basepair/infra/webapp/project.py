'''Project webapp api wrapper'''
import requests

# App imports
from .abstract import Abstract
from basepair.helpers import eprint

class Project(Abstract):
  '''Webapp Project class'''
  def __init__(self, cfg):
    super(Project, self).__init__(cfg)
    self.endpoint += 'projects/'

  def get_project_by_name(self, name, cache=False, params={}, verify=True): # pylint: disable=dangerous-default-value
    '''Get modules of an pipeline'''
    params.update(self.payload)
    try:
      response = requests.get(
        '{}?name__iexact={name}&owner__username={}'.format(self.endpoint, name, self.payload['username']),
        params=params,
        verify=verify,
      )
      parsed = self._parse_response(response)
      return parsed.get('objects')
    except requests.exceptions.RequestException as error:
      eprint('ERROR: {}'.format(error))
      return {'error': True, 'msg': error}
