'''AWS EC2 Wrappers'''

# General imports
import base64
import json
import os
import time
import re

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler
from basepair.modules.aws.service import Service

class EC2(Service):
  '''Wrapper for EC2 services'''
  def __init__(self, cfg):
    super().__init__(cfg, 'EC2')
    self.client = self.session.client(**{
      'config': Config(retries={'max_attempts': 10, 'mode': 'standard'}),
      'service_name': 'ec2',
    })
    self.default = {
      'ami': cfg.get('ami'),
      'availability_zone': cfg.get('availability_zone'),
      'instance_type': cfg.get('instance_type', 'm1.large'),
      'key_name': cfg.get('key_name'),
      'region': cfg.get('region'),
      'role_name': cfg.get('role'),
      'security_groups': cfg.get('security_groups') or ['worker'],
    }
    self.resource = self.session.resource('ec2')

  def attach_role(self, instance_id, role_name):
    '''Attach a role to instance'''
    try:
      response = self.client.associate_iam_instance_profile(
        IamInstanceProfile={'Name': role_name},
        InstanceId=instance_id,
      )
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to attach role {role_name} to instance {instance_id}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def describe_images(self, owners=None, filters=None):
    '''Look for images'''
    if owners is None:
      owners = []
    if filters is None:
      filters = []
    try:
      response = self.client.describe_images(Owners=owners, Filters=filters)
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to describe images due to error :\n{error}',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def get_instances(self, filters=None, ids=[], instance_id=None): # pylint: disable=dangerous-default-value
    '''Look for instances'''
    if instance_id:
      return self.resource.Instance(instance_id) # pylint: disable=no-member
    return self.resource.instances.filter(InstanceIds=ids, Filters=filters) # pylint: disable=no-member

  def get_security_group_by_name(self, group_name):
    '''Get security group by its name'''
    try:
      response = self.client.describe_security_groups(
        GroupNames=[group_name]
      )
      if response and response.get('SecurityGroups'):
        response = response.get('SecurityGroups')[0]
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get group {group_name}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def get_spot_price_history(self, options, use_cache=True):
    '''Look for the spot price history'''
    region = self.default.get('region')
    key = f"{options.get('availability_zone') or region}_{options.get('instance_type')}"
    cache_file = f'/tmp/{key}'
    ten_minutes_ago = time.time() - 600 # 600 seconds = 10 minutes
    if use_cache and os.path.isfile(cache_file):
      # reading the price from cache
      cache = {}
      with open(cache_file, 'r', encoding='utf-8') as file:
        cache = json.load(file)
      # expire the cache if needed
      filte_stats = os.stat(cache_file)
      if filte_stats.st_mtime < ten_minutes_ago:
        os.unlink(cache_file)
      # returning cached price
      return cache.get('price', [])

    try:
      response = self.client.describe_spot_price_history(
        AvailabilityZone=options.get('availability_zone', ''),
        EndTime=options.get('end_time'),
        InstanceTypes=[options.get('instance_type')],
        ProductDescriptions=options.get('product_description'),
        StartTime=options.get('start_time'),
      )
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': 'Not able to describe spot price history.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

    price = response.get('SpotPriceHistory', [])
    if price and use_cache:
      # removing Timestamp so we can json it
      for item in price:
        item.pop('Timestamp')
      with open(cache_file, 'w', encoding='utf-8') as file:
        json_content = json.dumps({'price': price})
        file.write(json_content)
    return price

  def launch_instance(self, settings): # pylint: disable=too-many-locals, too-many-branches
    '''Launch instance'''
    iam_role = settings.get('role_name') or self.default.get('role_name')
    security_groups = settings.get('security_groups') or self.default.get('security_groups')
    specification = {
      'BlockDeviceMappings': settings.get('block_device_map') or [],
      'ImageId': settings.get('ami', self.default.get('ami')),
      'InstanceType': settings.get('instance_type') or self.default.get('instance_type'),
      'SecurityGroupIds': self._get_security_groups_ids(security_groups),
      'UserData': base64.b64encode((settings.get('user_data') or '').encode()).decode('ascii'),
    }

    key_name = settings.get('key_name') or self.default.get('key_name')
    if key_name:
      specification['KeyName'] = key_name

    if iam_role:
      specification['IamInstanceProfile'] = {'Name': iam_role}

    availability_zone = settings.get('availability_zone') or self.default.get('availability_zone')
    if settings.get('subnet_id'):
      specification['SubnetId'] = settings.get('subnet_id')
    elif availability_zone:
      specification['Placement'] = {'AvailabilityZone': availability_zone}
      subnet_ids = settings.get('subnet_ids')
      if subnet_ids:
        for subnet_id in subnet_ids:
          subnet = self.resource.Subnet(subnet_id)
          if subnet.availability_zone == availability_zone:
            specification['SubnetId'] = subnet_id
            break
        else:
          return self.get_log_msg({
            'exception': None,
            'msg': 'No subnet found in the availability zone.',
          })

    price = settings.get('spot_price') or ''
    try:
      response = self.launch_spot(specification, price) if settings.get('spot') else self.launch_ondemand(specification)
      if not isinstance(response, dict):
        while (getattr(response, 'state', {}) or {}).get('Code') == 0:
          time.sleep(5)
          response.load()
        # update tags
        tags = []
        for tag, value in settings.get('tags', {}).items():
          tags.append({'Key': tag, 'Value': str(value)})
        response.create_tags(Tags=tags)

    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': 'Not able to launch instance.',
      })
      if ExceptionHandler.is_throttled_error(exception=error) or ExceptionHandler.is_insufficient_capacity_error(exception=error):
        raise error
    return response

  def launch_ondemand(self, specification):
    '''Start an ondemand intance'''
    specification['MaxCount'] = 1
    specification['MinCount'] = 1
    response = self.resource.create_instances(# pylint: disable=no-member
      **specification,
    )
    return next(iter(response), None)

  def launch_spot(self, specification, price=''):
    '''Request a spot intance and wait till it is available'''
    response = self.client.request_spot_instances(
      LaunchSpecification=specification,
      SpotPrice=price,
    )
    try:
      request = response.get('SpotInstanceRequests', [])[0]
      response = self._wait_for_spot_instance_request(request.get('SpotInstanceRequestId'))
    except KeyError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': 'Not able to request spot instance.',
      })
    return response

  def look_for_instance(self, instance_id, retry=10):
    '''Look for the instance with retry'''
    instance = None
    # we break the loop after n retries
    while retry > 0:
      time.sleep(15)
      instance = self.get_instances(instance_id=instance_id)
      if instance and instance.instance_id:
        break
      retry -= 1

    if retry == 0:
      instance = self.get_log_msg({
        'exception': 'Looking for instance stop after a few retries.',
        'msg': f'Not able to find the instance {instance_id}.',
      })
    return instance

  def tag(self, instance, tags):
    '''Helper to add tags to instances'''
    response = {
      'detail': None,
      'error': True,
      'msg': 'Not valid instance to tag.',
    }
    if hasattr(instance, 'create_tags'):
      try:
        tags_to_push = []
        for tag, value in tags.items():
          tags_to_push.append({'Key': tag, 'Value': str(value)})
        return instance.create_tags(Tags=tags_to_push)
      except ClientError as error:
        response = self.get_log_msg({
          'exception': error,
          'msg': 'Not able to tag instance.',
        })
        if ExceptionHandler.is_throttled_error(exception=error):
          raise error
    return response

  def _get_security_groups_ids(self, security_groups):
    '''If security group is of the format sg-words, returns it as the
    security group id, otherwise, translates groups name to groups ids.
    The group name translation works only if the security group is in
    the default VPC'''
    security_group_ids = []
    security_group_id_pattern = re.compile(r'^sg-\w+$')
    for group in security_groups:
      if security_group_id_pattern.match(group):
        # group is a security group id
        security_group_ids.append(group)
      else:
        # group is probably a security group name.
        # this works only if it is in the default vpc.
        group_obj = self.get_security_group_by_name(group)
        if group_obj.get('GroupId'):
          security_group_ids.append(group_obj.get('GroupId'))
    return security_group_ids

  def _wait_for_spot_instance_request(self, request_id, retry=4):
    '''Wait till we get the spot instance or an error'''
    time.sleep(10)
    request_instance = None
    try:
      requests = self.client.describe_spot_instance_requests(
        SpotInstanceRequestIds=[request_id]
      )
      request_instance = (requests or {}).get('SpotInstanceRequests', [])[0]
    except (ClientError, KeyError) as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to describe the spot instance request {request_id}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

    if request_instance:
      status = request_instance.get('Status', {})
      if status.get('Code') == 'fulfilled' and request_instance.get('InstanceId'):
        return self.look_for_instance(instance_id=request_instance.get('InstanceId'))

      error_status = [
        'canceled-before-fulfillment',
        'capacity-not-available',
        'capacity-oversubscribed',
        'failed',
        'instance-terminated-no-capacity',
        'price-too-low',
        'bad-parameters',
        'system-error'
      ]
      if retry == 0 or status.get('Code') in error_status:
        response = {
          'detail': status.get('Code') or 'Describe spot instance request expired.',
          'error': True,
          'msg': 'Not able to create spot instance.',
        }
        try:
          self.client.cancel_spot_instance_requests(SpotInstanceRequestIds=[request_id])
        except ClientError as error:
          response = self.get_log_msg({
            'exception': error,
            'msg': 'Not able to cancel the spot instance request.',
          })
          if ExceptionHandler.is_throttled_error(exception=error):
            raise error
        return response
    time.sleep(10)
    return self._wait_for_spot_instance_request(request_id, retry=retry - 1)