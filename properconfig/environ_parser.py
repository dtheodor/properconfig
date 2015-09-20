# -*- coding: utf-8 -*-
"""
Created by @dtheodor at 2015-09-06
"""
import os

from .common import ParseAttempt, failed_attempt, sources, SourceInfo


class EnvSource(SourceInfo):
    source = sources.ENV
    __slots__ = ("variable",)

    def __init__(self, variable):
        self.variable = variable


class EnvironParser(object):
    """Parse values from environment variables."""
    def __init__(self, prefix):
        self.prefix = prefix

    def cli_option_to_env_var(self, option):
        """Turns '--my-cli-option' into 'PREFIX_MY_CLI_OPTION'.
        """
        variable = option.lstrip("-").replace('-', '_').upper()
        return "{0}_{1}".format(self.prefix, variable)

    def parse(self, action):
        for string in action.option_strings:
            variable = self.cli_option_to_env_var(string)
            try:
                return ParseAttempt(
                    success=True,
                    value=[os.environ[variable]],
                    option_name=string,
                    source=EnvSource(variable=variable))
            except KeyError:
                pass
        return failed_attempt
