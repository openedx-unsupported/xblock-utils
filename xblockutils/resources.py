# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 Harvard, edX, OpenCraft
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3". If not, see <http://www.gnu.org/licenses/>.
#
"""
Helper class (ResourceLoader) for loading resources used by an XBlock
"""


import os
import sys
import warnings

import pkg_resources

import django
from django.template import Context, Template, Engine, base as TemplateBase

from mako.template import Template as MakoTemplate
from mako.lookup import TemplateLookup as MakoTemplateLookup


class ResourceLoader(object):
    """Loads resources relative to the module named by the module_name parameter."""
    def __init__(self, module_name):
        self.module_name = module_name

    def load_unicode(self, resource_path):
        """
        Gets the content of a resource
        """
        resource_content = pkg_resources.resource_string(self.module_name, resource_path)
        return unicode(resource_content, 'utf-8')

    def render_django_template(self, template_path, context=None, i18n_service=None):
        """
        Evaluate a django template by resource path, applying the provided context.
        """
        context = context or {}
        context['_i18n_service'] = i18n_service
        libraries = {
            'i18n': 'xblockutils.templatetags.i18n',
        }

        # For django 1.8, we have to load the libraries manually, and restore them once the template is rendered.
        _libraries = None
        if django.VERSION[0] == 1 and django.VERSION[1] == 8:
            _libraries = TemplateBase.libraries.copy()
            for library_name in libraries:
                library = TemplateBase.import_library(libraries[library_name])
                if library:
                    TemplateBase.libraries[library_name] = library
            engine = Engine()
        else:
            # Django>1.8 Engine can load the extra templatetag libraries itself
            # but we have to override the default installed libraries.
            from django.template.backends.django import get_installed_libraries
            installed_libraries = get_installed_libraries()
            installed_libraries.update(libraries)
            engine = Engine(libraries=installed_libraries)

        template_str = self.load_unicode(template_path)
        template = Template(template_str, engine=engine)
        rendered = template.render(Context(context))

        # Restore the original TemplateBase.libraries
        if _libraries is not None:
            TemplateBase.libraries = _libraries

        return rendered

    def render_mako_template(self, template_path, context=None):
        """
        Evaluate a mako template by resource path, applying the provided context
        """
        context = context or {}
        template_str = self.load_unicode(template_path)
        lookup = MakoTemplateLookup(directories=[pkg_resources.resource_filename(self.module_name, '')])
        template = MakoTemplate(template_str, lookup=lookup)
        return template.render(**context)

    def render_template(self, template_path, context=None):
        """
        This function has been deprecated. It calls render_django_template to support backwards compatibility.
        """
        warnings.warn(
            "ResourceLoader.render_template has been deprecated in favor of ResourceLoader.render_django_template"
        )
        return self.render_django_template(template_path, context)

    def render_js_template(self, template_path, element_id, context=None):
        """
        Render a js template.
        """
        context = context or {}
        return u"<script type='text/template' id='{}'>\n{}\n</script>".format(
            element_id,
            self.render_template(template_path, context)
        )

    def load_scenarios_from_path(self, relative_scenario_dir, include_identifier=False):
        """
        Returns an array of (title, xmlcontent) from files contained in a specified directory,
        formatted as expected for the return value of the workbench_scenarios() method.

        If `include_identifier` is True, returns an array of (identifier, title, xmlcontent).
        """
        base_dir = os.path.dirname(os.path.realpath(sys.modules[self.module_name].__file__))
        scenario_dir = os.path.join(base_dir, relative_scenario_dir)

        scenarios = []
        if os.path.isdir(scenario_dir):
            for template in sorted(os.listdir(scenario_dir)):
                if not template.endswith('.xml'):
                    continue
                identifier = template[:-4]
                title = identifier.replace('_', ' ').title()
                template_path = os.path.join(relative_scenario_dir, template)
                scenario = unicode(self.render_template(template_path, {"url_name": identifier}))
                if not include_identifier:
                    scenarios.append((title, scenario))
                else:
                    scenarios.append((identifier, title, scenario))

        return scenarios
