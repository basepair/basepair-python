'''AWS HealthOmics Workflow Wrapper'''

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.service import Service

class HOW(Service):
  '''Wrapper for Health Omics Workflow services'''

  def __init__(self, cfg):
    super().__init__(cfg, 'HOW')
    self.client = self.session.client(**{
      'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
      'service_name': 'omics',
    })

  def create_workflow(self, params):
    '''Create workflow'''
    try:
      response = self.client.create_workflow(**params)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to create HealthOmics workflow: {str(error)}.',
      })
      raise error
    return response

  def cancel_run(self, run_id):
    '''Cancel run'''
    try:
      response = self.client.cancel_run(id=run_id)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to cancel HealthOmics run: {str(error)}.',
      })
      raise error
    return response

  def delete_run(self, run_id):
    '''Delete run'''
    try:
      response = self.client.delete_run(id=run_id)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete HealthOmics run: {str(error)}.',
      })
      raise error
    return response

  def delete_workflow(self, params):
    '''Delete workflow'''
    try:
      response = self.client.delete_workflow(**params)
    except ClientError as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to delete HealthOmics workflow: {str(error)}.',
      })
      raise error
    return response

  def get_run(self, params):
    '''Get omics run'''
    try:
      return self.client.get_run(**params)
    except ClientError as error:
      self.get_log_msg({
        'exception': str(error),
        'msg': f'Not able to Get HealthOmics run id {params.get("id")}: {str(error)}.',
      })
      raise error
  
  def get_run_task(self, params):
    '''Get omics run task'''
    try:
      return self.client.get_run_task(**params)
    except ClientError as error:
      self.get_log_msg({
        'exception': str(error),
        'msg': f'Not able to Get HealthOmics run task id {params.get("id")}: {str(error)}.',
      })
      raise error

  def get_workflow(self, params):
    '''Get omics workflow'''
    try:
      return self.client.get_workflow(**params)
    except ClientError as error:
      self.get_log_msg({
        'exception': str(error),
        'msg': f'Not able to get HealthOmics workflow: {str(error)}.',
      })
      raise error

  def list_run_tasks(self, params):
    '''Get omics run list'''
    try:
      tasks = []
      while True:
        response = self.client.list_run_tasks(**params)
        next_token = response.get("nextToken")
        tasks += response.get('items')
        if next_token:
          params["startingToken"] = next_token
        else:
          break
      return tasks
    except ClientError as error:
      self.get_log_msg({
        'exception':error,
        'msg': f'Not able to Get HealthOmics run task list id {params.get("id")}: {str(error)}'
      })
      raise error

  def list_workflows(self, params):
    '''List omics workflows'''
    try:
      return self.client.list_workflows(**params)
    except ClientError as error:
      self.get_log_msg({
        'exception': str(error),
        'msg': f'Not able to list HealthOmics workflows: {str(error)}.',
      })
      raise error

  def start_run(self, params):
    '''Start omics workflow'''
    try:
      return self.client.start_run(**params)
    except ClientError as error:
      self.get_log_msg({
        'exception': str(error),
        'msg': f'Not able to start HealthOmics workflow id {params.get("workflowId")}: {str(error)}.',
      })
      raise error