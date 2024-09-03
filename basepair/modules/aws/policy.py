'''Helper with policy templates'''
import re

class Policy: # pylint: disable=too-few-public-methods
  '''Policy class'''

  @staticmethod
  def merge(policies):
    '''Helper to merge policies'''
    all_statements = []
    for policy in policies:
      all_statements += policy.get('Statement')
    return {
      'Statement': all_statements,
      'Version': '2012-10-17',
    }

  @staticmethod
  def ecr_bio_modules(repository_settings):
    '''ECR policy for worker'''
    return {
      'Statement': [{
        'Effect': 'Allow',
        'Action': [
          'ecr:BatchCheckLayerAvailability',
          'ecr:GetDownloadUrlForLayer',
          'ecr:GetRepositoryPolicy',
          'ecr:DescribeRepositories',
          'ecr:ListImages',
          'ecr:DescribeImages',
          'ecr:BatchGetImage',
          'ecr:GetLifecyclePolicy',
          'ecr:GetLifecyclePolicyPreview',
          'ecr:ListTagsForResource',
          'ecr:DescribeImageScanFindings'
        ],
        'Resource': [
          f"arn:aws:ecr:*:{repository_settings.get('account')}:repository/bio-*",
          f"arn:aws:ecr:*:{repository_settings.get('account')}:repository/takara*",
          f"arn:aws:ecr:*:{repository_settings.get('account')}:repository/vitrolife*",
        ],
        'Condition': {
          'StringEquals': {
            'aws:ResourceTag/Type': 'Bio'
          }
        }
      }, {
        'Effect': 'Allow',
        'Action': [
          'ecr:BatchCheckLayerAvailability',
          'ecr:GetDownloadUrlForLayer',
          'ecr:GetRepositoryPolicy',
          'ecr:DescribeRepositories',
          'ecr:ListImages',
          'ecr:DescribeImages',
          'ecr:BatchGetImage',
          'ecr:GetLifecyclePolicy',
          'ecr:GetLifecyclePolicyPreview',
          'ecr:ListTagsForResource',
          'ecr:DescribeImageScanFindings'
        ],
        'Resource': [
          f"arn:aws:ecr:*:{repository_settings.get('account')}:repository/worker*",
        ]
      }, {
        'Effect': 'Allow',
        'Action': 'ecr:GetAuthorizationToken',
        'Resource': '*'
      }, {
          'Effect': 'Allow',
          'Action': [
              'cloudwatch:PutMetricData',
              'ec2:DescribeVolumes',
              'ec2:DescribeTags',
              'logs:PutLogEvents',
              'logs:DescribeLogStreams',
              'logs:DescribeLogGroups',
              'logs:CreateLogStream',
              'logs:CreateLogGroup'
          ],
          'Resource': '*'
      }, {
          'Effect': 'Allow',
          'Action': ['ssm:GetParameter'],
          'Resource': 'arn:aws:ssm:*:*:parameter/AmazonCloudWatch-*'
      }],
      'Version': '2012-10-17'
    }

  @staticmethod
  def s3_delete_purpose(bucket, user_id):
    '''S3 policy to allow delete permission to their own uploaded samples'''
    resource = [
      f'arn:aws:s3:::{bucket}/uploads/{user_id}/*', # add sample_id to further restrict the user
    ]
    return {
      'Statement': [{
        'Action': ['s3:DeleteObject'],
        'Effect': 'Allow',
        'Resource': resource,
      }],
      'Version': '2012-10-17'
    }

  @staticmethod
  def hos_general_purpose(ho_region, reference_store_id, sequence_store_id):
    '''HOS policy template for general purpose'''
    return {
      'Statement': [
        {
          'Action': [
            "omics:BatchDeleteReadSet",
            "omics:DeleteReference",
            "omics:GetReadSet",
            "omics:GetReadSetExportJob",
            "omics:GetReadSetImportJob",
            "omics:GetReadSetMetadata",
            "omics:GetReferenceImportJob",
            "omics:GetReferenceMetadata",
            "omics:ListReadSets",
            "omics:ListReferences",
            "omics:StartReadSetActivationJob",
            "omics:StartReadSetExportJob",
            "omics:StartReadSetImportJob",
            "omics:StartReferenceImportJob",
          ],
          'Effect': 'Allow',
          'Resource': [
            f"arn:aws:omics:{ho_region}:*:referenceStore/{reference_store_id}/*",
            f"arn:aws:omics:{ho_region}:*:referenceStore/{reference_store_id}",
            f"arn:aws:omics:{ho_region}:*:sequenceStore/{sequence_store_id}/*",
            f"arn:aws:omics:{ho_region}:*:sequenceStore/{sequence_store_id}",
          ]
        }, {
          'Action': [
            "s3:GetObject",
            "s3:ListBucket"
          ],
          'Effect': 'Allow',
          'Resource': ['*'],
          'Condition': {
            'StringLike': {
              "s3:DataAccessPointArn": f"arn:aws:s3:{ho_region}:*"
            }
          }
        }, {
          'Action': ["kms:Decrypt"],
          'Effect': 'Allow',
          'Resource': [f"arn:aws:kms:{ho_region}:*:*"]
        }
      ]
    }

  @staticmethod
  def s3_general_purpose(bucket, reflib_buckets, user_id):
    '''S3 policy template for general purpose'''
    resource = [
      f'arn:aws:s3:::{bucket}/analyses/{user_id}/*',
      f'arn:aws:s3:::{bucket}/log/analyses/{user_id}/*',
      f'arn:aws:s3:::{bucket}/uploads/{user_id}/*',
    ]

    if 'vitrolife' in bucket:
      resource.append(f'arn:aws:s3:::{bucket}/vitrolife/*')
    if bool(re.search(r'(ivf|takara)', bucket)):
      resource.append(f'arn:aws:s3:::{bucket}/ivf/*')

    return {
      'Statement': [{
        'Action': 's3:ListBucket',
        'Effect': 'Allow',
        'Resource': [f'arn:aws:s3:::{bucket}'],
      }, {
        'Action': ['s3:GetObject', 's3:PutObject', 's3:PutObjectAcl', 's3:PutObjectTagging'],
        'Effect': 'Allow',
        'Resource': resource,
      }, {
        'Action': ['s3:GetObject'],
        'Effect': 'Allow',
        'Resource': [
          f'arn:aws:s3:::{reflib_bucket}/reflib/*' for reflib_bucket in reflib_buckets
        ],
      }, {
        'Action': 's3:ListBucket',
        'Effect': 'Allow',
        'Condition': {
          'StringLike': {
            's3:prefix': 'reflib/*'
          }
        },
        'Resource': [
          f'arn:aws:s3:::{reflib_bucket}' for reflib_bucket in reflib_buckets
        ],
      }],
      'Version': '2012-10-17'
    }

  @staticmethod
  def s3_upload(bucket, user_id):
    '''S3 Policy template for uploading purpose'''
    return {
      'Statement': [{
        'Effect': 'Allow',
        'Action': [
          's3:AbortMultipartUpload',
          's3:ListMultipartUploadParts',
          's3:PutObject',
        ],
        'Resource': [f'arn:aws:s3:::{bucket}/uploads/{user_id}/*']
      }],
      'Version': '2012-10-17'
    }

  @staticmethod
  def swf_worker(workflow_settings):
    '''SWF policy for worker'''
    return {
      'Statement': [{
        'Action': [
          'swf:RespondActivityTaskCompleted',
          'swf:PollForActivityTask',
        ],
        'Effect': 'Allow',
        'Resource': f"arn:aws:swf:*:*:/domain/{workflow_settings.get('domain')}"
      }],
      'Version': '2012-10-17'
    }

  @staticmethod
  def batch_worker():
    '''Batch policy for worker'''
    return {
      'Statement': [
        {
        'Effect': 'Allow',
        'Action': [
          "batch:CancelJob",
          "batch:DescribeComputeEnvironments",
          "batch:DescribeJobDefinitions",
          "batch:DescribeJobQueues",
          "batch:DescribeJobs",
          "batch:ListJobs",
          "batch:RegisterJobDefinition",
          "batch:SubmitJob",
          "batch:TagResource",
          "batch:TerminateJob",
        ],
        'Resource': "*",
        'Sid': "BatchAccess"
      }, {
        'Effect': 'Allow',
        'Action': [
          "ec2:DescribeInstanceAttribute",
          "ec2:DescribeInstanceStatus",
          "ec2:DescribeInstanceTypes",
          "ec2:DescribeInstances",
          "ecs:DescribeContainerInstances",
          "ecs:DescribeTasks",
        ],
        'Resource': "arn:aws:ecs:*:*:*",
        'Sid': "ECSDescribeTasks"
      }, {
        'Effect': 'Allow',
        'Action': [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:DescribeImageScanFindings",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetAuthorizationToken",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetLifecyclePolicy",
          "ecr:GetLifecyclePolicyPreview",
          "ecr:GetRepositoryPolicy",
          "ecr:ListImages",
          "ecr:ListTagsForResource",
        ],
        'Resource': 'arn:aws:ecr:*:*:repository/*',
        'Sid': "ECRAccess"
      }],
      'Version': '2012-10-17'
    }
