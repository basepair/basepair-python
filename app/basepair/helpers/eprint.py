'''Helper for print in stderr'''
from __future__ import print_function

# General imports
import sys

def eprint(*args, **kwargs):
  '''print in sys.stderr'''
  print(*args, file=sys.stderr, **kwargs)
