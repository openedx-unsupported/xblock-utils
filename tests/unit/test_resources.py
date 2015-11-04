# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 edX
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

import unittest

from mock import patch, DEFAULT

from xblockutils.resources import ResourceLoader


expected_string = u"""\
This is a simple template example.

This template can make use of the following context variables:
Name: {{name}}
List: {{items|safe}}

It can also do some fancy things with them:
Default value if name is empty: {{name|default:"Default Name"}}
Length of the list: {{items|length}}
Items of the list:{% for item in items %} {{item}}{% endfor %}
"""


example_context = {
    "name": "This is a fine name",
    "items": [1, 2, 3, 4, "a", "b", "c"],
}


expected_filled_template = u"""\
This is a simple template example.

This template can make use of the following context variables:
Name: This is a fine name
List: [1, 2, 3, 4, 'a', 'b', 'c']

It can also do some fancy things with them:
Default value if name is empty: This is a fine name
Length of the list: 7
Items of the list: 1 2 3 4 a b c
"""

example_id = "example-unique-id"

expected_filled_js_template = u"""\
<script type='text/template' id='example-unique-id'>
{}
</script>\
""".format(expected_filled_template)


another_template = u"""\
<explanation>This is an even simpler xml template.</explanation>
"""


simple_template = u"""\
<example>
    <title>This is a simple xml template.</title>
    <arguments>
        <url_name>simple_template</url_name>
    </arguments>
</example>
"""


expected_scenarios_with_identifiers = [
    ("another_template", "Another Template", another_template),
    ("simple_template", "Simple Template", simple_template),
]


expected_scenarios = [(t, c) for (i, t, c) in expected_scenarios_with_identifiers]


class TestResourceLoader(unittest.TestCase):
    def test_load_unicode(self):
        s = ResourceLoader(__name__).load_unicode("data/simple_django_template.txt")
        self.assertEquals(s, expected_string)

    def test_load_unicode_from_another_module(self):
        s = ResourceLoader("tests.unit.data").load_unicode("simple_django_template.txt")
        self.assertEquals(s, expected_string)

    def test_render_django_template(self):
        loader = ResourceLoader(__name__)
        s = loader.render_django_template("data/simple_django_template.txt", example_context)
        self.assertEquals(s, expected_filled_template)

    def test_render_mako_template(self):
        loader = ResourceLoader(__name__)
        s = loader.render_mako_template("data/simple_mako_template.txt", example_context)
        self.assertEquals(s, expected_filled_template)

    @patch('warnings.warn', DEFAULT)
    def test_render_template_deprecated(self, mock_warn):
        loader = ResourceLoader(__name__)
        s = loader.render_template("data/simple_django_template.txt", example_context)
        self.assertTrue(mock_warn.called)
        self.assertEquals(s, expected_filled_template)

    def test_render_js_template(self):
        loader = ResourceLoader(__name__)
        s = loader.render_js_template("data/simple_django_template.txt", example_id, example_context)
        self.assertEquals(s, expected_filled_js_template)

    def test_load_scenarios(self):
        loader = ResourceLoader(__name__)
        scenarios = loader.load_scenarios_from_path("data")
        self.assertEquals(scenarios, expected_scenarios)

    def test_load_scenarios_with_identifiers(self):
        loader = ResourceLoader(__name__)
        scenarios = loader.load_scenarios_from_path("data", include_identifier=True)
        self.assertEquals(scenarios, expected_scenarios_with_identifiers)
