'''AWS EFS Wrappers'''

# General import
import hashlib
import time
from datetime import datetime

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.handler.exception import ExceptionHandler
from basepair.modules.aws.service import Service

class EFS(Service): # pylint: disable=too-few-public-methods
	'''Wrapper for EFS services'''
	def __init__(self, cfg):
		super().__init__(cfg, 'EFS')
		self.client = self.session.client(**{
			'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
			'service_name': 'efs',
		})

	def create_file_system(self, options):
		'''Create a file system'''
		options['CreationToken'] = hashlib.md5(f'{datetime.now()}'.encode()).hexdigest()
		options['PerformanceMode'] = options.get('PerformanceMode') or 'generalPurpose'
		options['Encrypted'] = True
		options['ThroughputMode'] = options.get('ThroughputMode') or 'bursting'
		states = ['creating', 'updating']
		try:
			response = self.client.create_file_system(**options)
			check = response.get('LifeCycleState') in states
			while check:
				time.sleep(10)
				check_response = self.client.describe_file_systems(
					CreationToken=options['CreationToken'],
					MaxItems=1,
				)
				file_system = next(iter(check_response.get('FileSystems')), None)
				check = file_system.get('LifeCycleState') in states
		except ClientError as error:
			response = self.get_log_msg({
				'exception': error,
				'msg': 'Not able to create file system.',
			})
			if ExceptionHandler.is_throttled_error(exception=error):
				raise error
		return response

	def create_mount_target(self, file_system_id):
		'''create a moun target'''
		options = {
			'FileSystemId': file_system_id,
			'SecurityGroups': self.cfg.get('security_groups'),
		}
		for subnet_id in self.cfg.get('subnet_ids'):
			options['SubnetId'] = subnet_id
			try:
				response = self.client.create_mount_target(**options)
			except ClientError as error:
				response = self.get_log_msg({
					'exception': error,
					'msg': f'Not able to create mount target for given file system id {file_system_id}.',
				})
				if ExceptionHandler.is_throttled_error(exception=error):
					raise error
			if response.get('IpAddress'):
				break
		return response

	def delete(self, file_system_id):
		'''Delete a file system and all its mount targets'''
		# get all mount targets to delete them
		mount_targets = self.__get_all_mount_targets(file_system_id)
		try:
			for mount_target in mount_targets:
				self.client.delete_mount_target(MountTargetId=mount_target.get('MountTargetId'))
		except ClientError as error:
			self.get_log_msg({
				'exception': error,
				'msg': f'Not able to remove the mount targets for the given file system id {file_system_id}.',
			})
			if ExceptionHandler.is_throttled_error(exception=error):
				raise error

		while True:
			mount_targets = self.__get_all_mount_targets(file_system_id)
			if mount_targets:
				time.sleep(10)
				continue
			break

		# delete the file system
		try:
			self.client.delete_file_system(FileSystemId=file_system_id)
		except ClientError as error:
			self.get_log_msg({
				'exception': error,
				'msg': f'Not able to remove the given file system id {file_system_id}.',
			})
			if ExceptionHandler.is_throttled_error(exception=error):
				raise error

	def get_by_tags(self, tags):
		'''Helper to get the file systems by tag'''
		try:
			file_systems = self.__get_all_file_systems()
			for file_system in file_systems:
				could_be_this_one = True
				for file_system_tag in file_system.get('Tags'):
					key, value = file_system_tag.get('key'), file_system_tag.get('value')
					could_be_this_one = could_be_this_one and tags.get(key) == value
					if not could_be_this_one:
						break
				if could_be_this_one:
					return file_system
		except Exception as error: # pylint: disable=broad-except
			return self.get_log_msg({
				'exception': error,
				'msg': 'Not able to retrieve file systems to filter by tags',
			})
		return None

	# Private method
	def __get_full_list(self, arguments, error_msg, field, method):
		'''Helper to get full list of item of a given API method'''
		response = []
		while True:
			try:
				next_response = getattr(self.client, method)(**arguments)
				next_marker = next_response.get('NextMarker')
				arguments['Marker'] = next_marker
				response += next_response.get(field)
				should_exit = not bool(next_marker) or bool(next_response.get(field)) or len(next_response.get(field)) < 100
				if should_exit:
					break
			except ClientError as error:
				response = self.get_log_msg({
					'exception': error,
					'msg': error_msg,
				})
				if ExceptionHandler.is_throttled_error(exception=error):
					raise error
		return response


	def __get_all_file_systems(self):
		'''Retrieve the full list of file system'''
		return self.__get_full_list(
			arguments={},
			error_msg='Not able to retrieve all the file system.',
			field='FileSystems',
			method='describe_file_systems',
		)

	def __get_all_mount_targets(self, file_system_id):
		'''Retrieve the full list of mount targets'''
		return self.__get_full_list(
			arguments={'FileSystemId': file_system_id},
			error_msg=f'Not able to retrieve all the mount targets for the given file system id {file_system_id}.',
			field='MountTargets',
			method='describe_mount_targets',
		)
