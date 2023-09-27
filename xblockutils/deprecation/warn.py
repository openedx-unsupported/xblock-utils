"""
Utilities for warning about the use of deprecated package

See https://github.com/openedx/xblock-utils/issues/197 for details.
"""

import warnings


class DeprecatedPackageWarning(DeprecationWarning):
    """
    A warning that a deprecated package is being used.
    """

    def __init__(self, old_import, new_import):
        super().__init__()
        self.old_import = old_import
        self.new_import = new_import

    def __str__(self):
        return (
            "Please use import {self.new_import} instead of {self.old_import} as "
            "'xblock-utils' package has been deprecated and migrated within 'xblock' package. "
        ).format(self=self)


def warn_deprecated_package(old_import, new_import):
    """
    Warn that a package has been deprecated
    """
    warnings.warn(
        DeprecatedPackageWarning(old_import, new_import),
        stacklevel=3,  # Should surface the line that is doing the importing.
    )
