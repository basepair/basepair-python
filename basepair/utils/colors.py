#!/usr/bin/env python

from __future__ import print_function
from builtins import object


class color(object):
    HEADER = '\033[95m'
    BLUE = '\033[34m'
    CYAN = '\033[36;1m'
    GREEN = '\033[38;5;28m'
    BROWN = '\033[33m'
    RED = '\033[31m'
    ENDC = '\033[0m'

    @staticmethod
    def primary(text):
        return color.BLUE + text + color.ENDC

    @staticmethod
    def info(text):
        return color.CYAN + text + color.ENDC

    @staticmethod
    def success(text):
        return color.GREEN + text + color.ENDC

    @staticmethod
    def warning(text):
        return color.BROWN + text + color.ENDC

    @staticmethod
    def error(text):
        return color.RED + text + color.ENDC


if __name__ == '__main__':
    print(color.primary('primary'))
    print(color.primary('info'))
    print(color.success('success'))
    print(color.warning('warning'))
    print(color.error('error'))
    print('ok')
