INSTANCE_INFO = {
  't3.nano': {
    'num_core': 2,
    'num_hdd': 1,
  },
  't4g.nano': {
    'num_core': 2,
    'num_hdd': 1,
  },
  't3.micro': {
    'num_core': 2,
    'num_hdd': 1,
  },
  'm1.small': {
    'num_core': 1,
    'num_hdd': 1,
  },
  'm1.medium': {
    'num_core': 1,
    'num_hdd': 1,
  },
  'm1.large': {
    'num_core': 2,
    'num_hdd': 2,       # no good, now sooo good
  },
  'm1.xlarge': {
    'num_core': 4,
    'num_hdd': 4,
    'memory': 14,
  },
  'c1.medium': {
    'num_core': 2,
    'num_hdd': 1,
  },
  'm2.2xlarge': {
    'num_core': 4,
    'num_hdd': 1,
    'memory': 34.2,
  },
  'm2.4xlarge': {
    'num_core': 8,
    'num_hdd': 2,
    'memory': 67,
  },
  'm3.medium': {
    'num_core': 1,
    'num_hdd': 1,
  },
  'm3.large': {
    'num_core': 2,
    'num_hdd': 1,
  },
  'm3.xlarge': {
    'num_core': 4,
    'num_hdd': 2,
  },
  'm3.2xlarge': {
    'num_core': 8,
    'num_hdd': 2,
  },
  'c3.large': {
    'num_core': 2,
    'num_hdd': 2,
  },
  'c3.xlarge': {
    'num_core': 4,
    'num_hdd': 2,
  },
  'c3.2xlarge': {
    'num_core': 8,
    'num_hdd': 2,
    'memory': 14,
  },
  'c3.4xlarge': {
    'num_core': 16,
    'num_hdd': 2,
    'memory': 29,
  },
  'c3.8xlarge': {
    'num_core': 32,
    'num_hdd': 2,
    'memory': 59,
  },
  'c4.8xlarge': {
    'num_core': 32,
    'num_hdd': 0,
    'memory': 59,
  },
  'c6a.32xlarge': {
    'num_core': 128,
    'memory': 256,
    'num_hdd': 1
  },
  'r3.large': {
    'num_core': 2,
    'num_hdd': 1,
  },
  'r3.xlarge': {
    'num_core': 4,
    'num_hdd': 1,
  },
  'r3.2xlarge': {
    'num_core': 8,
    'num_hdd': 1,
  },
  'r3.4xlarge': {
    'num_core': 16,
    'num_hdd': 1,
  },
  'm5d.large': {
    'num_core': 2,
    'memory': 8,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based':  True,
  },
  'm5d.xlarge': {
    'num_core': 4,
    'memory': 16,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based':  True,
  },
  'm5d.2xlarge': {
    'num_core': 8,
    'memory': 32,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based':  True,
  },
  'm5d.4xlarge': {
    'num_core': 16,
    'memory': 63,
    'num_hdd': 2,
    'nvme': True,
    'nitro_based':  True,
  },
  'm5d.8xlarge': {
    'num_core': 32,
    'memory': 128,
    'num_hdd': 2,
    'nvme': True,
    'nitro_based': True,
  },
  'm5d.12xlarge': {
    'num_core': 48,
    'memory': 192,
    'num_hdd': 2,
    'nvme': True,
    'nitro_based': True,
  },
  'c5d.large': {
    'num_core': 2,
    'memory': 4,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based': True,
  },
  'c5d.xlarge': {
    'num_core': 4,
    'memory': 8,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based': True,
  },
  'c5d.2xlarge': {
    'num_core': 8,
    'memory': 16,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based': True,
  },
  'c5d.4xlarge': {
    'num_core': 16,
    'memory': 32,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based': True,
  },
  'c5d.9xlarge': {
    'num_core': 36,
    'memory': 72,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based': True,
  },
  'c5d.18xlarge': {
    'num_core': 72,
    'memory': 144,
    'num_hdd': 2,
    'nvme': True,
    'nitro_based': True,
  },
  'c5d.24xlarge': {
    'num_core': 96,
    'memory': 192,
    'num_hdd': 4,
    'nvme': True,
    'nitro_based': True,
  },
  'i3.2xlarge': {
    'num_core': 8,
    'memory': 61,
    'num_hdd': 1,
    'nvme': True,
  },
  'i3.4xlarge': {
    'num_core': 16,
    'memory': 122,
    'num_hdd': 2,
    'nvme': True,
  },
  'i3.8xlarge': {
    'num_core': 32,
    'memory': 242,
    'num_hdd': 4,   # nvme1n1
    'nvme': True,
  },
  'i3.16xlarge': {
    'num_core': 64,
    'memory': 488,
    'num_hdd': 8,   # nvme1n1
    'nvme': True,
  },
  'i3en.xlarge': {
    'num_core': 4,
    'memory': 32,
    'num_hdd': 1,   # nvme1n1
    'nvme': True,
    'nitro_based': True,
  },
  'i4i.2xlarge': {
      'num_core': 8,
      'memory': 64,
      'num_hdd': 1,
      'nvme': True,
      'nitro_based': True,
  },
  'i4i.4xlarge': {
      'num_core': 16,
      'memory': 128,
      'num_hdd': 1,
      'nvme': True,
      'nitro_based': True,
  },
  'i4i.8xlarge': {
      'num_core': 32,
      'memory': 256,
      'num_hdd': 2,
      'nvme': True,
      'nitro_based': True,
  },
  'i4i.12xlarge': {
      'num_core': 48,
      'memory': 384,
      'num_hdd': 3,
      'nvme': True,
      'nitro_based': True,
  },
  'i4i.16xlarge': {
      'num_core': 64,
      'memory': 512,
      'num_hdd': 4,
      'nvme': True,
      'nitro_based': True,
  },
  'r6id.16xlarge': {
    'num_core': 64,
    'memory': 512,
    'num_hdd': 2,
    'nvme': True,
    'nitro_based': True,
  },
  'm6gd.medium': {
    'num_core': 1,
    'memory': 4,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based': True,
  },
  'c6gd.large': {
    'num_core': 2,
    'memory': 4,
    'num_hdd': 1,
    'nvme': True,
    'nitro_based': True,
  },
  'x1e.16xlarge': {
    'num_core': 64,
    'memory': 1952,
    'num_hdd': 1,
    'nvme': False,
    'nitro_based': False,
  },
}
