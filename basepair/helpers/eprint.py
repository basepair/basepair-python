'''Helper for print in stderr'''

# General imports
import sys

def eprint(*args, **kwargs):
  '''print in sys.stderr'''
  print(*args, file=sys.stderr, **kwargs)
