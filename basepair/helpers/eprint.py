'''Helper for print in stderr'''

def eprint(*args, **kwargs):
  '''print in sys.stderr'''
  print(*args, file=sys.stderr, **kwargs)
