import unittest

from xblockutils.base_test import SeleniumBaseTest


class TestSeleniumBaseTest(SeleniumBaseTest):
    module_name = __name__
    default_css_selector = "div.vertical"

    def test_true(self):
        self.go_to_page("Simple Scenario")


class TestSeleniumBaseTestWithoutDefaultSelector(SeleniumBaseTest):
    module_name = __name__

    def test_true(self):
        self.go_to_page("Simple Scenario", "div.vertical")
