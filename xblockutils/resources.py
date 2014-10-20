import os
import sys

import pkg_resources
from django.template import Context, Template


class ResourceLoader(object):
    """Loads resources relative to the module named by the module_name parameter."""
    def __init__(self, module_name):
        self.module_name = module_name

    def load_unicode(self, resource_path):
        """
        Gets the content of a resource
        """
        resource_content = pkg_resources.resource_string(self.module_name, resource_path)
        return unicode(resource_content)

    def render_template(self, template_path, context={}):
        """
        Evaluate a template by resource path, applying the provided context
        """
        template_str = self.load_unicode(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def render_js_template(self, template_path, element_id, context={}):
        """
        Render a js template.
        """
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
            for template in os.listdir(scenario_dir):
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
