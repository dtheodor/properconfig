# -*- coding: utf-8 -*-
"""
author: dtheodor
created: 2015-Aug-03


"""
import os
from argparse import ArgumentParser


class ConfigParser(ArgumentParser):
    """Parses arguments from environment variables and files as well as from
    the command line.
    """
    def error(self, message):
        print message
        raise Exception(message)

    def parse_args(self, args=None, namespace=None):
        super(ConfigParser, self).parse_args(args=args, namespace=namespace)
        pass

class TypeParser(object):
    """Responsible for converting the raw value to the proper type"""

class EnvironParser(object):
    """Parse values from environment variables."""
    def __init__(self, prefix):
        self.prefix = prefix

    def parse(self, variable):
        return os.environ[variable]


class FileParser(object):
    """Parse values from a file."""

parser = ConfigParser(description="test")
parser.add_argument('-v', '--verbose', type=int, required=True)

if __name__ == "__main__":
    args = parser.parse_args()
    print args
