'''AWS Exception handler class'''

class ExceptionHandler:
  '''Helper class'''
  def __init__(self):
    pass

  @staticmethod
  def is_insufficient_capacity_error(exception=None):
    '''Check if a insufficient capacity error'''
    if exception:
      return (getattr(exception, 'response', {})).get('Error', {}).get('Code') == 'InsufficientInstanceCapacity'
    return None

  @staticmethod
  def is_throttled_error(exception=None):
    '''Check if a throttled error'''
    if exception:
      return (getattr(exception, 'response', {})).get('Error', {}).get('Code') in ExceptionHandler.get_throttled_error_codes()
    return None

  @staticmethod
  def get_throttled_error_codes():
    '''Get a list of all throttled error codes'''
    return [
      'Throttling',
      'ThrottlingException',
      'ThrottledException',
      'RequestThrottledException',
      'TooManyRequestsException',
      'ProvisionedThroughputExceededException',
      'TransactionInProgressException',
      'RequestLimitExceeded',
      'BandwidthLimitExceeded',
      'LimitExceededException',
      'ReadTimeoutError',
      'RequestThrottled',
      'SlowDown',
      'PriorRequestNotComplete',
      'EC2ThrottledException',
    ]
