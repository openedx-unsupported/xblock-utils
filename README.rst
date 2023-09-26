xblock-utils: Various utilities for XBlocks
###########################################

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

These are a collection of utility functions, base test classes and
documentation that are useful for any XBlocks.


⚠️ Deprecation Notice ⚠️
************************

**Effective Date:** September 26, 2023

**Repository Migration:**
This `xblock-utils` repository has been `deprecated <https://github.com/openedx/xblock-utils/issues/197>`_ as of September 26, 2023, and the code and documentation have been migrated to the `Xblock <https://github.com/openedx/XBlock>`_ repository.

This decision was made to streamline and consolidate our codebase.

The migration process was completed through this Pull Request: `PR #669 <https://github.com/openedx/XBlock/pull/669>`_

**Archival**: We are going to archive the `xblock-utils` repository. This means that it will become read-only, and no further updates or changes will be accepted.

We appreciate your understanding and cooperation during this transition. If you have any questions or concerns, please don't hesitate to reach out to us through the `XBlock` repository's issue tracker.

Thank you for your continued support and contributions to the Open edX community.


Getting Started
***************

Developing
==========

One Time Setup
--------------
.. code-block::

  # Clone the repository
  git clone git@github.com:openedx/xblock-utils.git
  cd xblock-utils

  # Set up a virtualenv with the same name as the repo and activate it
  # Here's how you might do that if you have virtualenvwrapper setup.
  mkvirtualenv -p python3.8 xblock-utils


Every time you develop something in this repo
---------------------------------------------
.. code-block::

  # Activate the virtualenv
  # Here's how you might do that if you're using virtualenvwrapper.
  workon xblock-utils

  # Grab the latest code
  git checkout master
  git pull

  # Install/update the dev requirements
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make test 

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim ...

  # Temporary until https://github.com/openedx/xblock-utils/issues/199 is resolved
  mkdir var
  touch var/workbench.log

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the tests and quality checks
  make test

  # Commit all your changes
  git commit ...
  git push

  # Open a PR and ask for review.

Deploying
=========

This component is automatically deployed to PyPI whenever new GitHub releases are made.

To deploy this library.

#. Update the version in ``xblockutils/__init__.py`` based on semantic versioning.

#. Create a new GitHub release with a tag matching the version.

#. Automation should build and deploy the version to PyPI

Getting Help
************

Documentation
=============

Start by going through `the documentation`_.  If you need more help see below.

.. _the documentation: https://docs.openedx.org/projects/xblock-utils

More Help
=========

If you're having trouble, we have discussion forums at
https://discuss.openedx.org where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an issue in this
repository with as many details about the issue you are facing as you
can provide.

https://github.com/openedx/xblock-utils/issues

For more information about these options, see the `Project Getting Help`_ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _Project Getting Help: https://openedx.org/getting-help

License
*******

The code in this repository is licensed under the AGPLv3 unless
otherwise noted.

Please see `the LICENSE <LICENSE>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/xblock-utils

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/xblock-utils.svg
    :target: https://pypi.python.org/pypi/xblock-utils/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/xblock-utils/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/openedx/xblock-utils/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/openedx/xblock-utils/coverage.svg?branch=main
    :target: https://codecov.io/github/openedx/xblock-utils?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/xblock-utils/badge/?version=latest
    :target: https://docs.openedx.org/projects/xblock-utils/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/xblock-utils.svg
    :target: https://pypi.python.org/pypi/xblock-utils/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/openedx/xblock-utils.svg
    :target: https://github.com/openedx/xblock-utils/blob/main/LICENSE
    :alt: License

.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen

More Documentation
******************

StudioEditableXBlockMixin
=========================

.. code:: python

    from xblockutils.studio_editable import StudioEditableXBlockMixin

This mixin will automatically generate a working ``studio_view`` form
that allows content authors to edit the fields of your XBlock. To use,
simply add the class to your base class list, and add a new class field
called ``editable_fields``, set to a tuple of the names of the fields
you want your user to be able to edit.

.. code:: python

    @XBlock.needs("i18n")
    class ExampleBlock(StudioEditableXBlockMixin, XBlock):
        ...
        mode = String(
            display_name="Mode",
            help="Determines the behaviour of this component. Standard is recommended.",
            default='standard',
            scope=Scope.content,
            values=('standard', 'crazy')
        )
        editable_fields = ('mode', 'display_name')

That's all you need to do. The mixin will read the optional
``display_name``, ``help``, ``default``, and ``values`` settings from
the fields you mention and build the editor form as well as an AJAX save
handler.

If you want to validate the data, you can override
``validate_field_data(self, validation, data)`` and/or
``clean_studio_edits(self, data)`` - see the source code for details.

Supported field types:

* Boolean:
  ``field_name = Boolean(display_name="Field Name")``
* Float:
  ``field_name = Float(display_name="Field Name")`` 
* Integer:
  ``field_name = Integer(display_name="Field Name")`` 
* String:
  ``field_name = String(display_name="Field Name")`` 
* String (multiline):
  ``field_name = String(multiline_editor=True, resettable_editor=False)``
* String (html):
  ``field_name = String(multiline_editor='html', resettable_editor=False)``

Any of the above will use a dropdown menu if they have a pre-defined
list of possible values.

* List of unordered unique values (i.e. sets) drawn from a small set of
  possible values:
  ``field_name = List(list_style='set', list_values_provider=some_method)``

  - The ``List`` declaration must include the property ``list_style='set'`` to
    indicate that the ``List`` field is being used with set semantics.
  - The ``List`` declaration must also define a ``list_values_provider`` method
    which will be called with the block as its only parameter and which must
    return a list of possible values.
* Rudimentary support for Dict, ordered List, and any other JSONField-derived field types

  - ``list_field = List(display_name="Ordered List", default=[])``
  - ``dict_field = Dict(display_name="Normal Dict", default={})``

Supported field options (all field types):

* ``values`` can define a list of possible options, changing the UI element
  to a select box. Values can be set to any of the formats `defined in the
  XBlock source code <https://github.com/openedx/XBlock/blob/master/xblock/fields.py>`__:
  
  - A finite set of elements: ``[1, 2, 3]``
  - A finite set of elements where the display names differ from the values::

        [
            {"display_name": "Always", "value": "always"},
            {"display_name": "Past Due", "value": "past_due"},
        ]
  - A range for floating point numbers with specific increments:
    ``{"min": 0 , "max": 10, "step": .1}``
  - A callable that returns one of the above. (Note: the callable does
    *not* get passed the XBlock instance or runtime, so it cannot be a
    normal member function)
* ``values_provider`` can define a callable that accepts the XBlock
  instance as an argument, and returns a list of possible values in one
  of the formats listed above.
* ``resettable_editor`` - defaults to ``True``. Set ``False`` to hide the
  "Reset" button used to return a field to its default value by removing
  the field's value from the XBlock instance.

Basic screenshot: |Screenshot 1|

StudioContainerXBlockMixin
==========================

.. code:: python

    from xblockutils.studio_editable import StudioContainerXBlockMixin

This mixin helps to create XBlocks that allow content authors to add,
remove, or reorder child blocks. By removing any existing
``author_view`` and adding this mixin, you'll get editable,
re-orderable, and deletable child support in Studio. To enable authors to
add arbitrary blocks as children, simply override ``author_edit_view`` 
and set ``can_add=True`` when calling ``render_children`` - see the 
source code. To restrict authors so they can add only specific types of
child blocks or a limited number of children requires custom HTML.

An example is the mentoring XBlock: |Screenshot 2|

SeleniumXBlockTest
==================

.. code:: python

    from xblockutils.base_test import SeleniumXBlockTest

This is a base class that you can use for writing Selenium integration
tests that are hosted in the XBlock SDK (Workbench).

Here is an example:

.. code:: python

    class TestStudentView(SeleniumXBlockTest):
        """
        Test the Student View of MyCoolXBlock
        """
        def setUp(self):
            super(TestStudentView, self).setUp()
            self.set_scenario_xml('<mycoolblock display_name="Test Demo Block" field2="hello" />')
            self.element = self.go_to_view("student_view")

        def test_shows_field_2(self):
            """
            The xblock should display the text value of field2.
            """
            self.assertIn("hello", self.element.text)

StudioEditableBaseTest
======================

.. code:: python

    from xblockutils.studio_editable_test import StudioEditableBaseTest

This is a subclass of ``SeleniumXBlockTest`` that adds a few helper
methods useful for testing the ``studio_view`` of any XBlock using
``StudioEditableXBlockMixin``.

child\_isinstance
=================

.. code:: python

    from xblockutils.helpers import child_isinstance

If your XBlock needs to find children/descendants of a particular
class/mixin, you should use

.. code:: python

    child_isinstance(self, child_usage_id, SomeXBlockClassOrMixin)

rather than calling

.. code:: python

    ``isinstance(self.runtime.get_block(child_usage_id), SomeXBlockClassOrMixin)``.

On runtimes such as those in edx-platform, ``child_isinstance`` is
orders of magnitude faster.

.. |Screenshot 1| image:: https://cloud.githubusercontent.com/assets/945577/6341782/7d237966-bb83-11e4-9344-faa647056999.png
.. |Screenshot 2| image:: https://cloud.githubusercontent.com/assets/945577/6341803/d0195ec4-bb83-11e4-82f6-8052c9f70690.png

XBlockWithSettingsMixin
=======================

This mixin provides access to instance-wide XBlock-specific configuration settings.
See [wiki page](https://github.com/openedx/xblock-utils/wiki/Settings-and-theme-support#accessing-xblock-specific-settings) for details

ThemableXBlockMixin
===================

This mixin provides XBlock theming capabilities built on top of XBlock-specific settings.
See [wiki page](https://github.com/openedx/xblock-utils/wiki/Settings-and-theme-support#theming-support) for details
