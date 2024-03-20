'''AWS market place metering'''
# App imports
from botocore.exceptions import ClientError
from basepair.modules.aws.service import Service

class MMetering(Service):
  '''Wrapper for Marketplace services'''
  def __init__(self, cfg):
    super().__init__(cfg, service_name='Marketplace metering')
    self.client = self.session.client(**{'service_name': 'meteringmarketplace'})
    self.product_code = cfg.get('product_code')

  def resolve_customer(self, registration_token):
    '''resolve customer method'''
    try:
      response = self.client.resolve_customer(RegistrationToken=registration_token)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to resolve customer with token - {registration_token}.',
      })
      raise error
    return response

  def send_batch_credit_usage(self, usage_record):
    '''send credit usage records method'''
    try:
      response = self.client.batch_meter_usage(UsageRecords=usage_record, ProductCode=self.product_code)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to send credit usage records - {str(usage_record)}',
      })
      raise error
    return response
