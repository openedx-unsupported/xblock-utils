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
"""
Base classes for Selenium or bok-choy based integration tests of XBlocks.
"""

import time

from selenium.webdriver.support.ui import WebDriverWait
from workbench.runtime import WorkbenchRuntime
from workbench.scenarios import SCENARIOS, add_xml_scenario, remove_scenario
from workbench.test.selenium_test import SeleniumTest

from .resources import ResourceLoader


class SeleniumXBlockTest(SeleniumTest):
    """
    Base class for using the workbench to test XBlocks with Selenium or bok-choy.

    If you want to test an XBlock that's not already installed into the python environment,
    you can use @XBlock.register_temp_plugin around your test method[s].
    """
    timeout = 10  # seconds

    def setUp(self):
        super(SeleniumXBlockTest, self).setUp()
        # Delete all scenarios from the workbench:
        import workbench.urls  # Trigger initial scenario load. pylint: disable=unused-variable
        SCENARIOS.clear()
        # Disable CSRF checks on XBlock handlers:
        import workbench.views
        workbench.views.handler.csrf_exempt = True

    def wait_until_visible(self, elem):
        """ Wait until the given element is visible """
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: e.is_displayed(), u"{} should be visible".format(elem.text))

    def wait_until_hidden(self, elem):
        """ Wait until the DOM element elem is hidden """
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: not e.is_displayed(), u"{} should be hidden".format(elem.text))

    def wait_until_disabled(self, elem):
        """ Wait until the DOM element elem is disabled """
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: not e.is_enabled(), u"{} should be disabled".format(elem.text))

    def wait_until_clickable(self, elem):
        """ Wait until the DOM element elem is display and enabled """
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: e.is_displayed() and e.is_enabled(), u"{} should be clickable".format(elem.text))

    def wait_until_text_in(self, text, elem):
        """ Wait until the specified text appears in the DOM element elem """
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: text in e.text, u"{} should be in {}".format(text, elem.text))

    def wait_until_html_in(self, html, elem):
        """ Wait until the specified HTML appears in the DOM element elem """
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: html in e.get_attribute('innerHTML'),
                   u"{} should be in {}".format(html, elem.get_attribute('innerHTML')))

    def wait_until_exists(self, selector):
        """ Wait until the specified selector exists on the page """
        wait = WebDriverWait(self.browser, self.timeout)
        wait.until(
            lambda driver: driver.find_element_by_css_selector(selector),
            u"Selector '{}' should exist.".format(selector)
        )

    @staticmethod
    def set_scenario_xml(xml):
        """ Reset the workbench to have only one scenario with the specified XML """
        SCENARIOS.clear()
        add_xml_scenario("test", "Test Scenario", xml)

    def go_to_view(self, view_name='student_view', student_id="student_1"):
        """
        Navigate to the page `page_name`, as listed on the workbench home
        Returns the DOM element on the visited page located by the `css_selector`
        """
        url = self.live_server_url + '/scenario/test/{}/'.format(view_name)
        if student_id:
            url += '?student={}'.format(student_id)
        self.browser.get(url)
        return self.browser.find_element_by_css_selector('.workbench .preview > div.xblock-v1:first-child')

    def load_root_xblock(self, student_id="student_1"):
        """
        Load (in Python) the XBlock at the root of the current scenario.
        """
        dom_node = self.browser.find_element_by_css_selector('.workbench .preview > div.xblock-v1:first-child')
        usage_id = dom_node.get_attribute('data-usage')
        runtime = WorkbenchRuntime(student_id)
        return runtime.get_block(usage_id)


class SeleniumBaseTest(SeleniumXBlockTest):
    """
    Selenium Base Test for loading a whole folder of XML scenarios and then running tests.
    This is kept for compatibility, but it is recommended that SeleniumXBlockTest be used
    instead, since it is faster and more flexible (specifically, scenarios are only loaded
    as needed, and can be defined inline with the tests).
    """
    module_name = None  # You must set this to __name__ in any subclass so ResourceLoader can find scenario XML files
    default_css_selector = None  # Selector used by go_to_page to return the XBlock DOM element
    relative_scenario_path = 'xml'  # Path from the module (module_name) to the secnario XML files

    @property
    def _module_name(self):
        """ Internal method to access module_name with a friendly warning if it's unset """
        if self.module_name is None:
            raise NotImplementedError("Overwrite cls.module_name in your derived class.")
        return self.module_name

    @property
    def _default_css_selector(self):
        """ Internal method to access default_css_selector with a warning if it's unset """
        if self.default_css_selector is None:
            raise NotImplementedError("Overwrite cls.default_css_selector in your derived class.")
        return self.default_css_selector

    def setUp(self):
        super(SeleniumBaseTest, self).setUp()
        # Use test scenarios:
        loader = ResourceLoader(self._module_name)
        scenarios_list = loader.load_scenarios_from_path(self.relative_scenario_path, include_identifier=True)
        for identifier, title, xml in scenarios_list:
            add_xml_scenario(identifier, title, xml)
            self.addCleanup(remove_scenario, identifier)

        # Suzy opens the browser to visit the workbench
        self.browser.get(self.live_server_url)

        # She knows it's the site by the header
        header1 = self.browser.find_element_by_css_selector('h1')
        self.assertEqual(header1.text, 'XBlock scenarios')

    def go_to_page(self, page_name, css_selector=None, view_name=None):
        """
        Navigate to the page `page_name`, as listed on the workbench home
        Returns the DOM element on the visited page located by the `css_selector`
        """
        if css_selector is None:
            css_selector = self._default_css_selector

        self.browser.get(self.live_server_url)
        target_url = self.browser.find_element_by_link_text(page_name).get_attribute('href')
        if view_name:
            target_url += '{}/'.format(view_name)
        self.browser.get(target_url)
        time.sleep(1)
        block = self.browser.find_element_by_css_selector(css_selector)
        return block
