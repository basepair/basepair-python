'''AWS SWF Wrappers'''

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler
from basepair.modules.aws.service import Service

class SWF(Service):
  '''Wrapper for SWF services'''
  def __init__(self, cfg):
    super().__init__(cfg, 'SWF')
    self.client = self.session.client(**{
      'config': Config(read_timeout=120, retries={'max_attempts': 0, 'mode': 'standard'}),
      'service_name': 'swf',
    })
    self.domain = cfg.get('domain')

  def describe(self, run_id, workflow_id):
    '''Describe workflow'''
    try:
      return self.client.describe_workflow_execution(
        domain=self.domain,
        execution={
          'workflowId': workflow_id,
          'runId': run_id,
        }
      )
    except (ClientError, self.client.exceptions.OperationNotPermittedFault, self.client.exceptions.UnknownResourceFault) as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to describe workflow id {workflow_id}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
      return response

  def get_all_workflow_execution_history(self, domain, run_id, workflow_id):
    '''Get all workflow execution history'''
    try:
      response = self.client.get_workflow_execution_history(
        domain=domain,
        execution={
          'runId': run_id,
          'workflowId': workflow_id,
        },
      )
      while 'nextPageToken' in response:
        next_page = self.client.get_workflow_execution_history(
          domain=domain,
          execution={
            'runId': run_id,
            'workflowId': workflow_id,
          },
          nextPageToken=response.get('nextPageToken')
        )
        response['events'] += next_page.get('events', [])
        response['nextPageToken'] = next_page.get('nextPageToken')
    except (ClientError, self.client.exceptions.OperationNotPermittedFault, self.client.exceptions.UnknownResourceFault) as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to get workflow execution history for workflow id {workflow_id}.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def poll_activity_task(self, domain, identity, task_list):
    '''Poll activity task'''
    try:
      response = self.client.poll_for_activity_task(
        domain=domain,
        identity=identity,
        taskList={'name': task_list},
      )
    except (ClientError, self.client.exceptions.OperationNotPermittedFault, self.client.exceptions.UnknownResourceFault) as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to poll for activity task for task list {task_list} ({domain}).',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def poll_all_for_decision_task(self, identity, task_list):
    '''Poll all for decision task'''
    try:
      response = self.client.poll_for_decision_task(
        domain=self.domain,
        identity=identity,
        taskList={'name': task_list},
      )
      while 'nextPageToken' in response:
        next_page = self.client.poll_for_decision_task(
          domain=self.domain,
          identity=identity,
          nextPageToken=response.get('nextPageToken'),
          taskList={'name': task_list},
        )
        response['events'] += next_page.get('events', [])
        response['nextPageToken'] = next_page.get('nextPageToken')
    except (ClientError, self.client.exceptions.OperationNotPermittedFault, self.client.exceptions.UnknownResourceFault) as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': f'Not able to poll for decision task for task list {task_list} ({self.domain}).',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def respond_activity_task_completed(self, result, token):
    '''Respond activity task completed'''
    try:
      response = self.client.respond_activity_task_completed(
        result=result,
        taskToken=token,
      )
    except (ClientError, self.client.exceptions.OperationNotPermittedFault, self.client.exceptions.UnknownResourceFault) as error:
      response = self.get_log_msg({
        'exception': error,
        'msg': 'Not able to respond activity task completed.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
    return response

  def respond_decision_task(self, task_token, decisions):
    '''Respond decision task'''
    try:
      self.client.respond_decision_task_completed(
        decisions=decisions,
        taskToken=task_token,
      )
    except (ClientError, self.client.exceptions.OperationNotPermittedFault, self.client.exceptions.UnknownResourceFault) as error:
      self.get_log_msg({
        'exception': error,
        'msg': 'Not able to respond decision task completed.',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error

  def start(self, options):
    '''Start workflow execution'''
    workflow = options.get('workflow', {})
    workflow_id = workflow.pop('id', None)
    try:
      return self.client.start_workflow_execution(
        domain=self.domain,
        executionStartToCloseTimeout=options.get('execution_timeout', '31536000'),
        input=options.get('input'),
        tagList=options.get('tag_list', []),
        taskList={'name': options.get('task', {}).get('list')},
        taskStartToCloseTimeout=options.get('task', {}).get('timeout', '31536000'),
        workflowId=workflow_id,
        workflowType=workflow,
      )
    except (ClientError, self.client.exceptions.OperationNotPermittedFault, self.client.exceptions.UnknownResourceFault) as error:
      code = (getattr(error, 'response', {})).get('Error', {}).get('Code')
      msg = 'Workflow execution already started fault.' if code == 'WorkflowExecutionAlreadyStartedFault' \
        else f'Not able to start workflow execution id {workflow_id} ({self.domain}).'
      response = self.get_log_msg({
        'exception': error,
        'msg': msg,
      })
      if code == 'LimitExceededException':
        raise error
      return response

  def terminate(self, workflow_id):
    '''Terminate workflow execution'''
    try:
      self.client.terminate_workflow_execution(
        domain=self.domain,
        workflowId=workflow_id,
      )
    except (ClientError, self.client.exceptions.OperationNotPermittedFault, self.client.exceptions.UnknownResourceFault) as error:
      self.get_log_msg({
        'exception': error,
        'msg': f'Not able to terminate workflow execution id {workflow_id} ({self.domain}).',
      })
      if ExceptionHandler.is_throttled_error(exception=error):
        raise error
