'''AWS SQS Wrappers'''

# General import
import json

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler
from basepair.modules.aws.service import Service

class SQS(Service):
  '''Wrapper for SQS services'''
  def __init__(self, cfg):
    super().__init__(cfg, 'SQS')
    self.client = self.session.client(**{
      'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
      'service_name': 'sqs',
    })
    self.queue = cfg.get('queue')
    self.wait_time = cfg.get('wait_time', 20)

  def clear(self):
    '''Clear all message in queue'''
    self.client.purge_queue(QueueUrl=self.get_queue_url(self.queue))

  def create(self, queue):
    '''Create a queue'''
    try:
      self.client.create_queue(QueueName=queue)
      response = self.client.get_queue_url(QueueName=queue)
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to create queue {queue}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response.get('QueueUrl')

  def delete_message(self, handler):
    '''Delete a message from queue'''
    queue_url = self.get_queue_url(self.queue)
    if isinstance(queue_url, dict) and queue_url.get('error'):
      return queue_url

    try:
      response = self.client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=handler
      )
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to remove message from queue {self.queue}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def get_message(self, visibility_time_out=1500, wait_time=None):
    '''Read one message from queue'''
    wait_time = wait_time or self.wait_time
    try:
      res = self.client.receive_message(
        QueueUrl=self.get_queue_url(self.queue),
        MaxNumberOfMessages=1,
        VisibilityTimeout=visibility_time_out,
        WaitTimeSeconds=wait_time,
      )
      message = res.get('Messages')[0]
      response = {
        'body': message.get('Body'),
        'handler': message.get('ReceiptHandle'),
        'id': message.get('MessageId'),
      }
    except (ClientError, IndexError) as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get message from queue {self.queue}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def get_messages(self, limit=10, visibility_time_out=1500, wait_time=None):
    '''Read messages from queue'''
    wait_time = wait_time or self.wait_time
    try:
      res = self.client.receive_message(
        AttributeNames=['All'],
        QueueUrl=self.get_queue_url(self.queue),
        MaxNumberOfMessages=limit if limit <= 10 else 10,
        VisibilityTimeout=visibility_time_out,
        WaitTimeSeconds=wait_time,
      )
      response = [{
        'attributes': message.get('Attributes'),
        'body': message.get('Body'),
        'handler': message.get('ReceiptHandle'),
        'id': message.get('MessageId'),
      } for message in res.get('Messages')] if res.get('Messages') else []

    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get messages from queue {self.queue}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def get_queue_url(self, queue, create=True):
    '''Get the queue URL from queue name'''
    try:
      res = self.client.get_queue_url(QueueName=queue)
      response = res and res.get('QueueUrl')
    except ClientError as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get queue url for queue {self.queue}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      if create:
        self.get_log_msg({
          'exception': None,
          'msg': f'Creating new queue {self.queue}.',
          'msg_type': 'info',
        })
        self.create(queue)
        response = self.get_queue_url(queue, create=False)
    return response

  def send_message(self, msg, delay=0, queue=None):
    '''Send message'''
    queue = queue or self.queue
    queue_url = self.get_queue_url(queue)
    if isinstance(queue_url, dict) and queue_url.get('error'):
      return queue_url

    msg.pop('delay', None)
    if delay > 900:
      msg['delay'] = delay - 900
      delay = 900

    if isinstance(queue_url, str):
      try:
        response = self.client.send_message(
          DelaySeconds=delay,
          MessageBody=json.dumps(msg),
          QueueUrl=queue_url,
        )
      except ClientError as error:
        response = self.get_log_msg({
          'exception': error,
          'msg': f'Not able to send message to queue {queue}.',
        })
        if ExceptionHandler.is_throttled_error(exception=error):
          raise error
    return response

  def set_queue(self, queue):
    '''Set default queue'''
    self.queue = queue

  def update_message_visibility(self, handler, timeout):
    '''Update the message visibility timeout'''
    queue_url = self.get_queue_url(self.queue)
    try:
      self.client.change_message_visibility(
        QueueUrl=queue_url,
        ReceiptHandle=handler,
        VisibilityTimeout=timeout,
      )
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': 'Not able to update the message visibility timeout.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
