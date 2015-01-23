import os
import sys
import time

import pkg_resources

from django.template import Context, Template

from selenium.webdriver.support.ui import WebDriverWait

from workbench import scenarios
from workbench.test.selenium_test import SeleniumTest

from .resources import ResourceLoader


class SeleniumBaseTest(SeleniumTest):
    module_name = None
    default_css_selector = None
    relative_scenario_path = 'xml'
    timeout = 10  # seconds

    @property
    def _module_name(self):
        if self.module_name is None:
            raise NotImplementedError("Overwrite cls.module_name in your derived class.")
        return self.module_name

    @property
    def _default_css_selector(self):
        if self.default_css_selector is None:
            raise NotImplementedError("Overwrite cls.default_css_selector in your derived class.")
        return self.default_css_selector

    def setUp(self):
        super(SeleniumBaseTest, self).setUp()

        # Use test scenarios
        self.browser.get(self.live_server_url)  # Needed to load tests once
        scenarios.SCENARIOS.clear()
        loader = ResourceLoader(self._module_name)
        scenarios_list = loader.load_scenarios_from_path(self.relative_scenario_path, include_identifier=True)
        for identifier, title, xml in scenarios_list:
            scenarios.add_xml_scenario(identifier, title, xml)
            self.addCleanup(scenarios.remove_scenario, identifier)

        # Suzy opens the browser to visit the workbench
        self.browser.get(self.live_server_url)

        # She knows it's the site by the header
        header1 = self.browser.find_element_by_css_selector('h1')
        self.assertEqual(header1.text, 'XBlock scenarios')

    def wait_until_hidden(self, elem):
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: not e.is_displayed(), u"{} should be hidden".format(elem.text))

    def wait_until_disabled(self, elem):
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: not e.is_enabled(), u"{} should be disabled".format(elem.text))

    def wait_until_clickable(self, elem):
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: e.is_displayed() and e.is_enabled(), u"{} should be clickable".format(elem.text))

    def wait_until_text_in(self, text, elem):
        wait = WebDriverWait(elem, self.timeout)
        wait.until(lambda e: text in e.text, u"{} should be in {}".format(text, elem.text))

    def wait_until_exists(self, selector):
        wait = WebDriverWait(self.browser, self.timeout)
        wait.until(lambda driver: driver.find_element_by_css_selector(selector), u"Selector '{}' should exist.".format(selector))

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
            target_url += '%s/' % view_name
        self.browser.get(target_url)
        time.sleep(1)
        block = self.browser.find_element_by_css_selector(css_selector)
        return block
