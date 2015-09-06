# -*- coding: utf-8 -*-
"""
Created by @dtheodor at 2015-09-06
"""
import os
from ConfigParser import ConfigParser, DEFAULTSECT, \
    Error as ConfigParserError

from .common import ParseAttempt, failed_attempt


def get_local_filename(prog):
    return os.path.join(os.path.expanduser("~"), prog)


class FileParser(object):
    """Parses values from an .ini file.

    Uses the ConfigParser module.
    """
    def __init__(self, fp, filename=None):
        if filename is None:
            try:
                filename = fp.name
            except AttributeError:
                filename = "<Unknown filename>"
        self.filename = filename
        config = self.config = ConfigParser()
        config.readfp(fp)

    @classmethod
    def from_filename(cls, filename):
        with open(filename) as f:
            return FileParser(f, filename)

    @staticmethod
    def cli_option_to_file_option(option):
        """Turns '--my-cli-option' into 'my-cli-option'."""
        return option.lstrip("-")

    def parse(self, action):
        for string in action.option_strings:
            option = self.cli_option_to_file_option(string)
            try:
                # TODO: change DEFAULTSECT to program name
                value = self.config.get(DEFAULTSECT, option)
                return ParseAttempt(
                    success=True,
                    value=[value],
                    option_name=string,
                    source="Filename: '{}', Option: '{}'".format(
                        self.filename or '<Unknown filename>', option))
            except ConfigParserError:
                pass
        return failed_attempt
