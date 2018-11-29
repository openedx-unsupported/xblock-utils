# -*- coding: utf-8 -*-
"""
This module contains a mixin that allows third party XBlocks to
easily have multiple templates that instructors can choose from
before editing the XBlock
"""
import logging
import os
import yaml

from pkg_resources import (
    resource_exists,
    resource_listdir,
    resource_string,
    resource_isdir,
)

log = logging.getLogger(__name__)


class ResourceTemplatesXBlockMixin(object):
    """
    Gets the templates associated w/ a containing cls. The cls must have a 'template_dir_name' attribute.
    It finds the templates as directly in this directory under 'templates'.
    """
    template_packages = [__name__]

    @classmethod
    def templates(cls):
        """
        Returns a list of dictionary field: value objects that describe possible
        templates that can be used to seed a module of this type.

        Expects a class attribute template_dir_name that defines the directory
        inside the 'templates' resource directory to pull templates from
        """
        templates = []
        dirname = cls.get_template_dir()
        if dirname is not None:
            for pkg in cls.template_packages:
                if not resource_isdir(pkg, dirname):
                    continue
                for template_file in resource_listdir(pkg, dirname):
                    if not template_file.endswith('.yaml'):
                        log.warning(u'Skipping unknown template file %s', template_file)
                        continue
                    template_content = resource_string(pkg, os.path.join(dirname, template_file))
                    template = yaml.safe_load(template_content)
                    template['template_id'] = template_file
                    templates.append(template)
        return templates

    @classmethod
    def get_template_dir(cls):
        """
        Get the first valid directory name from the template packages.
        :return: The directory name that hosts the templates.
        """
        if not getattr(cls, 'template_dir_name', None):
            return None

        dirname = os.path.join('templates', cls.template_dir_name)
        for package in cls.template_packages:
            if resource_isdir(package, dirname):
                return dirname

        log.warning(u'No resource directory %s found when loading %s templates', dirname, cls.__name__)
        return None

    @classmethod
    def get_template(cls, template_id):
        """
        Get a single template by the given id (which is the file name identifying
        it w/in the class's template_dir_name)

        """
        dirname = cls.get_template_dir()
        if dirname is not None:
            path = os.path.join(dirname, template_id)
            for pkg in cls.template_packages:
                if resource_exists(pkg, path):
                    template_content = resource_string(pkg, path)
                    template = yaml.safe_load(template_content)
                    template['template_id'] = template_id
                    return template
