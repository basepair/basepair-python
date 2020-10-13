'''Helper to filter sets of data'''

class SetFilter:
  '''Helper class to filter list'''
  @staticmethod
  def diff(a_set, b_set):
    '''Filter by not intersection'''
    return not set(b_set).intersection(set(a_set))

  @staticmethod
  def exact(a_set, b_set):
    '''Filter by eq'''
    return set(a_set) == set(b_set)

  @staticmethod
  def subset(a_set, b_set):
    '''Filter by intersection'''
    return set(a_set).intersection(set(b_set))
