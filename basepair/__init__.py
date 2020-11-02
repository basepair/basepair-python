'''set up basepair package'''
from __future__ import print_function
import sys

import requests

from .utils import colors
# from .api import basepair

__title__ = 'basepair'
__version__ = '1.5.0'
__copyright__ = 'Copyright [2017] - [2020] Basepair INC'


JSON_URL = 'https://pypi.python.org/pypi/{}/json'.format(__title__)
try:
    resp = requests.get(JSON_URL, timeout=1)
    if resp.status_code == 200:
        latest_version = resp.json()['info']['version']
        if latest_version != __version__:
            print(colors.color.warning(
                'WARNING: The latest version of basepair package is {}. '
                'Please upgrade to avail the latest features and bug-fixes'
                ''.format(latest_version)), file=sys.stderr)
except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
    print('warning: no internet', file=sys.stderr)


def connect(*args, **kwargs):
    '''return basepair package'''
    from basepair.api import BpApi
    return BpApi(*args, **kwargs)
