
from django.template import Context, Template
from xblockutils.resources import ResourceLoader

loader = ResourceLoader(__name__)


def render_template(template_path, context, **kwargs):
    file_path = "tests/integration/template_stubs/" + template_path

    with open(file_path, 'r') as tpl_file:
        template_str = tpl_file.read().replace('\n', '')
        template = Template(template_str)
        return template.render(Context(context))
