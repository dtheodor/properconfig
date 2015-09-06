"""
Created by @dtheodor at 2015-09-06
"""
from collections import namedtuple

ParseAttempt = namedtuple("ParseAttempt", [
    "success", "value", "option_name", "source"])

failed_attempt = ParseAttempt(success=False,
                              value=None,
                              option_name=None,
                              source=None)