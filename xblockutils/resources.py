import pkg_resources
from django.template import Context, Template


class ResourceLoader(object):
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
