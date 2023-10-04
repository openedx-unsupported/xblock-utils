"""Deprecated package support."""
# pylint: disable=useless-suppression,line-too-long,redefined-builtin,wildcard-import,
# pylint: disable=wrong-import-position,wrong-import-order

from xblockutils.deprecation.warn import warn_deprecated_package

warn_deprecated_package(
    'xblockutils.templatetags.i18n',
    'xblock.utils.templatetags.i18n'
)

from xblock.utils.templatetags.i18n import *
