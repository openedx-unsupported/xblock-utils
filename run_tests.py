#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run tests for XBlock-utils
"""

from __future__ import absolute_import
import os
import sys

if __name__ == "__main__":
    # Use the workbench settings file:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workbench.settings")
    # Configure a range of ports in case the default port of 8081 is in use
    os.environ.setdefault("DJANGO_LIVE_TEST_SERVER_ADDRESS", "localhost:8081-8099")

    from django.core.management import execute_from_command_line
    args = sys.argv[1:]
    paths = [arg for arg in args if arg[0] != '-']
    if not paths:
        paths = ["tests/"]
    options = [arg for arg in args if arg not in paths]
    if not os.path.exists('var'):
        os.makedirs('var')
    execute_from_command_line([sys.argv[0], "test"] + paths + options)
