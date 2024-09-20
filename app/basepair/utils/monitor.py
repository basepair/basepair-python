# monitors multiple files for modification
# can check for modification of one or all of them
#
# usage:
# monitor = Monitor()
# monitor.monitor('decider.py')

# if monitor.is_modified('decider.py'):     # check one specific file
# if monitor.is_modified():                 # check all monitored files

from builtins import object
import os

class Monitor(object):
    def __init__(self, filename=None):
        self.last_modified = {}
        if filename:
            self.monitor(filename)

    def monitor(self, filename):
        self.last_modified[filename] = os.path.getmtime(filename)
    
    def is_modified(self, filename=None):
        if filename:
            return self.is_modified_filename(filename)
        else:
            # if any single file is modified, return True
            for filename in list(self.last_modified.keys()):
                if self.is_modified_filename(filename):
                    return True
            return False

    def is_modified_filename(self, filename):
        if os.path.getmtime(filename) > self.last_modified[filename]:
            self.last_modified[filename] = os.path.getmtime(filename)
            return True
        else:
            return False
