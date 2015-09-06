# -*- coding: utf-8 -*-
"""
author: dtheodor
created: 2015-Aug-03
"""
from collections import namedtuple

ParseAttempt = namedtuple("ParseAttempt", [
    "success", "value", "option_name", "source"])

failed_attempt = ParseAttempt(success=False,
                              value=None,
                              option_name=None,
                              source=None)