"""AWS HealthOmics Storage Wrappers"""

# General imports
import uuid

# Libs imports
from botocore.client import Config
from botocore.exceptions import ClientError

# Module imports
from basepair.modules.aws.service import Service


class HOS(Service):
    """Wrapper for Health Omics Storage services"""

    def __init__(self, cfg):
        super().__init__(cfg, 'HOS')
        self.client = self.session.client(**{
            'config': Config(retries={'max_attempts': 0, 'mode': 'standard'}),
            'service_name': 'omics',
        })
        self.sequence_store_id = cfg.get('sequence_store_id')
        self.reference_store_id = cfg.get('reference_store_id')
        self.role_arn = cfg.get('role_arn')

    def batch_delete_read_set(self, read_set_ids):
        """Delete read sets"""
        try:
            response = self.client.batch_delete_read_set(sequenceStoreId=self.sequence_store_id, ids=read_set_ids)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to delete HealthOmics read sets: {str(error)}.',
            })
            raise error
        return response

    def delete_reference(self, reference_id):
        """Delete reference"""
        try:
            response = self.client.delete_reference(id=reference_id, referenceStoreId=self.reference_store_id)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to delete HealthOmics reference: {str(error)}.',
            })
            raise error
        return response

    def get_read_set_export_job(self, job_id):
        """Get export job"""
        try:
            response = self.client.get_read_set_export_job(id=job_id, sequenceStoreId=self.sequence_store_id)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to get HealthOmics export job information: {str(error)}.',
            })
            raise error
        return response

    def get_read_set_import_job(self, job_id):
        """Get import job"""
        try:
            response = self.client.get_read_set_import_job(id=job_id, sequenceStoreId=self.sequence_store_id)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to get HealthOmics import job information: {str(error)}.',
            })
            raise error
        return response

    def get_read_set_metadata(self, read_set_id):
        """Get read set metadata"""
        try:
            response = self.client.get_read_set_metadata(id=read_set_id, sequenceStoreId=self.sequence_store_id)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to get HealthOmics read set metadata: {str(error)}.',
            })
            raise error
        return response

    def get_reference_import_job(self, job_id):
        """Get reference import job"""
        try:
            response = self.client.get_reference_import_job(id=job_id, referenceStoreId=self.reference_store_id)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to get HealthOmics reference import job information: {str(error)}.',
            })
            raise error
        return response

    def get_reference_metadata(self, reference_id):
        """Get reference metadata"""
        try:
            response = self.client.get_reference_metadata(id=reference_id, referenceStoreId=self.reference_store_id)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to get HealthOmics reference metadata: {str(error)}.',
            })
            raise error
        return response

    def list_read_sets(self, filters):
        """Get read sets list"""
        try:
            response = self.client.list_read_sets(sequenceStoreId=self.sequence_store_id, filter=filters)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to list HealthOmics read sets: {str(error)}.',
            })
            raise error
        return response

    def list_references(self, filters):
        """Get references list"""
        try:
            response = self.client.list_references(referenceStoreId=self.reference_store_id, filter=filters)
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to list HealthOmics references: {str(error)}.',
            })
            raise error
        return response

    def start_read_set_activation_job(self, read_set_ids):
        """Start read set activation job"""
        try:
            sources = [{'readSetId': read_set_id} for read_set_id in read_set_ids]
            client_token = str(uuid.uuid4())
            return self.client.start_read_set_activation_job(
                sequenceStoreId=self.sequence_store_id,
                clientToken=client_token,
                sources=sources
            )
        except ClientError as error:
            self.get_log_msg({
                'exception': str(error),
                'msg': f'Not able to start HealthOmics read set activation job: {str(error)}.',
            })
            raise error

    def start_read_set_export_job(self, destination, sources):
        """Start export job"""
        try:
            client_token = str(uuid.uuid4())
            response = self.client.start_read_set_export_job(
                sequenceStoreId=self.sequence_store_id,
                destination=destination,
                roleArn=self.role_arn,
                clientToken=client_token,
                sources=sources
            )
        except ClientError as error:
            self.get_log_msg({
                'exception': error,
                'msg': f'Not able to start HealthOmics export job: {str(error)}.',
            })
            raise error
        return response

    def start_read_set_import_job(self, sources):
        """Start import job"""
        try:
            client_token = str(uuid.uuid4())
            return self.client.start_read_set_import_job(
                sequenceStoreId=self.sequence_store_id,
                roleArn=self.role_arn,
                clientToken=client_token,
                sources=sources
            )
        except ClientError as error:
            self.get_log_msg({
                'exception': str(error),
                'msg': f'Not able to start HealthOmics import job: {str(error)}.',
            })
            raise error

    def start_reference_import_job(self, sources):
        """Start reference import job"""
        try:
            client_token = str(uuid.uuid4())
            return self.client.start_reference_import_job(
                referenceStoreId=self.reference_store_id,
                roleArn=self.role_arn,
                clientToken=client_token,
                sources=sources
            )
        except ClientError as error:
            self.get_log_msg({
                'exception': str(error),
                'msg': f'Not able to start HealthOmics reference import job: {str(error)}.',
            })
            raise error
