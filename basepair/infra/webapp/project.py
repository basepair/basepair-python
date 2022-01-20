'''Project webapp api wrapper'''
import requests

# App imports
from basepair.helpers import eprint
from .abstract import Abstract

class Project(Abstract):
  '''Webapp Project class'''
  def __init__(self, cfg):
    super(Project, self).__init__(cfg)
    self.endpoint += 'projects/'

  def get_project_by_name(self, name, params={}, verify=True): # pylint: disable=dangerous-default-value
    '''Get modules of an pipeline'''
    params.update(self.payload)
    try:
      response = requests.get(
        f"{self.endpoint}?name__iexact={name}&owner__username={self.payload['username']}",
        params=params,
      )
      parsed = self._parse_response(response)
      return parsed.get('objects')
    except requests.exceptions.RequestException as error:
      eprint(f'ERROR: {error}')
      return {'error': True, 'msg': error}
