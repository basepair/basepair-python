import unittest

from lib import *
from cases import *


class SamplesTest(BaseTest):

    def test_create_sample(self):
        for case in sample_cases:
            new_sample_id = self.bp.create_sample(case)
            new_sample = self.bp.get_sample(uid=new_sample_id)
            # pp.pprint(new_sample)
            compare_info(case, new_sample)


if __name__ == '__main__':
    unittest.main()
