"""Deprecated package support."""
# pylint: disable=useless-suppression,line-too-long,redefined-builtin,wildcard-import,
# pylint: disable=wrong-import-position,wrong-import-order

from xblockutils.deprecation.warn import warn_deprecated_package

warn_deprecated_package(
    'xblockutils.publish_event',
    'xblock.utils.publish_event'
)

from xblock.utils.publish_event import *
