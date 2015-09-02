"""
Tests for StudioEditableXBlockMixin
"""
from selenium.webdriver.support.ui import WebDriverWait
from xblockutils.base_test import SeleniumXBlockTest


class CommonBaseTest(SeleniumXBlockTest):
    """
    Base class of StudioEditableBaseTest and StudioContainerWithNestedXBlocksBaseTest
    """
    def fix_js_environment(self):
        """ Make the Workbench JS runtime more compatibile with Studio's """
        # Mock gettext()
        self.browser.execute_script('window.gettext = function(t) { return t; };')
        # Mock runtime.notify() so we can watch for notify events like 'save'
        self.browser.execute_script(
            'window.notifications = [];'
            'window.RuntimeProvider.getRuntime(1).notify = function() {'
            '    window.notifications.push(arguments);'
            '};'
        )

    def dequeue_runtime_notification(self, wait_first=True):
        """
        Return the oldest call from JavaScript to block.runtime.notify() that we haven't yet
        seen here in Python-land. Waits for a notification unless wait_first is False.
        """
        if wait_first:
            self.wait_for_runtime_notification()
        return self.browser.execute_script('return window.notifications.shift();')

    def wait_for_runtime_notification(self):
        """ Wait until runtime.notify() has been called """
        wait = WebDriverWait(self.browser, self.timeout)
        wait.until(lambda driver: driver.execute_script('return window.notifications.length > 0;'))


class StudioEditableBaseTest(CommonBaseTest):
    """
    Base class that can be used for integration tests of any XBlocks that use
    StudioEditableXBlockMixin
    """
    def click_save(self, expect_success=True):
        """ Click on the save button """
        # Click 'Save':
        self.browser.find_element_by_link_text('Save').click()
        # Before saving the block changes, the runtime should get a 'save' notice:
        notification = self.dequeue_runtime_notification()
        self.assertEqual(notification[0], "save")
        self.assertEqual(notification[1]["state"], "start")
        if expect_success:
            notification = self.dequeue_runtime_notification()
            self.assertEqual(notification[0], "save")
            self.assertEqual(notification[1]["state"], "end")

    def get_element_for_field(self, field_name):
        """ Given the name of a field, return the DOM element for its form control """
        selector = "li.field[data-field-name={}] .field-data-control".format(field_name)
        return self.browser.find_element_by_css_selector(selector)

    def click_reset_for_field(self, field_name):
        """ Click the reset button next to the specified setting field """
        selector = "li.field[data-field-name={}] .setting-clear".format(field_name)
        self.browser.find_element_by_css_selector(selector).click()


class StudioContainerWithNestedXBlocksBaseTest(CommonBaseTest):
    """
    Base class that can be used for integration tests of any XBlocks that use
    StudioContainerWithNestedXBlocksMixin
    """
    def get_add_buttons(self):
        """
        Gets add buttons in author view
        """
        selector = ".add-xblock-component .new-component a.add-xblock-component-button"
        return self.browser.find_elements_by_css_selector(selector)
