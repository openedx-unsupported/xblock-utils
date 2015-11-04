import datetime
import textwrap
import mock
import pytz
from selenium.common.exceptions import NoSuchElementException
from xblock.core import XBlock
from xblock.fields import Boolean, Dict, Float, Integer, List, String, DateTime
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage
from tests.integration.utils import render_template
from xblockutils.studio_editable import StudioEditableXBlockMixin, StudioContainerWithNestedXBlocksMixin, \
    NestedXBlockSpec
from xblockutils.studio_editable_test import StudioEditableBaseTest, StudioContainerWithNestedXBlocksBaseTest


class EditableXBlock(StudioEditableXBlockMixin, XBlock):
    """
    A basic Studio-editable XBlock (for use in tests)
    """
    CATEGORY = "editable"
    STUDIO_LABEL = "Editable Block"

    color = String(default="red")
    count = Integer(default=42)
    comment = String(default="")
    date = DateTime(default=datetime.datetime(2014, 5, 14, tzinfo=pytz.UTC))
    editable_fields = ('color', 'count', 'comment', 'date')

    def student_view(self, context):
        return Fragment()

    def validate_field_data(self, validation, data):
        """
        A validation method to check that 'count' is positive and prevent
        swearing in the 'comment' field.
        """
        if data.count < 0:
            validation.add(ValidationMessage(ValidationMessage.ERROR, u"Count cannot be negative"))
        if "damn" in data.comment.lower():
            validation.add(ValidationMessage(ValidationMessage.ERROR, u"No swearing allowed"))


class UnawareXBlock(XBlock):
    """
    A naive XBlock for use in tests
    """

    color = String(default="red")

    def student_view(self, context):
        return Fragment()


class TestEditableXBlock_StudioView(StudioEditableBaseTest):
    """
    Test the Studio View created for EditableXBlock
    """

    def set_up_root_block(self):
        self.set_scenario_xml('<editable />')
        self.go_to_view("studio_view")
        self.fix_js_environment()
        return self.load_root_xblock()

    def assert_unchanged(self, block, orig_field_values=None, explicitly_set=False):
        """
        Check that all field values on 'block' match with either the value in orig_field_values
        (if provided) or the default value.
        If 'explitly_set' is False (default) it asserts that no fields have an explicit value
        set. If 'explititly_set' is True it expects all fields to be explicitly set.
        """
        for field_name in block.editable_fields:
            expected_value = orig_field_values[field_name] if orig_field_values else block.fields[field_name].default
            self.assertEqual(getattr(block, field_name), expected_value)
            self.assertEqual(block.fields[field_name].is_set_on(block), explicitly_set)

    @XBlock.register_temp_plugin(EditableXBlock, "editable")
    def test_no_changes_with_defaults(self):
        """
        If we load the edit form and then save right away, there should be no changes.
        """
        block = self.set_up_root_block()
        orig_values = {field_name: getattr(block, field_name) for field_name in EditableXBlock.editable_fields}
        self.click_save()
        self.assert_unchanged(block, orig_values)

    @XBlock.register_temp_plugin(EditableXBlock, "editable")
    def test_no_changes_with_values_set(self):
        """
        If the XBlock already has explicit values set, and we load the edit form and then save
        right away, there should be no changes.
        """
        block = self.set_up_root_block()
        block.color = "green"
        block.count = 5
        block.comment = "Hello"
        block.date = datetime.datetime(2014, 6, 17, tzinfo=pytz.UTC)
        block.save()
        orig_values = {field_name: getattr(block, field_name) for field_name in EditableXBlock.editable_fields}
        # Reload the page:
        self.go_to_view("studio_view")
        self.fix_js_environment()

        self.click_save()
        block = self.load_root_xblock()  # Need to reload the block to bypass its cache
        self.assert_unchanged(block, orig_values, explicitly_set=True)

    @XBlock.register_temp_plugin(EditableXBlock, "editable")
    def test_explicit_overrides(self):
        """
        Test that we can override the defaults with the same value as the default, and that the
        value will be saved explicitly.
        """
        block = self.set_up_root_block()
        self.assert_unchanged(block)

        field_names = EditableXBlock.editable_fields
        # It is crucial to this test that at least one of the fields is a String field with
        # an empty string as its default value:
        defaults = set([block.fields[field_name].default for field_name in field_names])
        self.assertIn(u'', defaults)

        for field_name in field_names:
            control = self.get_element_for_field(field_name)
            control.send_keys('9999')  # In case the field is blank and the new value is blank, this forces a change
            control.clear()
            control.send_keys(str(block.fields[field_name].default))

        self.click_save()
        self.assert_unchanged(block, explicitly_set=True)

    @XBlock.register_temp_plugin(EditableXBlock, "editable")
    def test_set_and_reset(self):
        """
        Test that we can set values, save, then reset to defaults.
        """
        block = self.set_up_root_block()
        self.assert_unchanged(block)

        for field_name in EditableXBlock.editable_fields:
            if field_name == 'date':
                continue
            color_control = self.get_element_for_field(field_name)
            color_control.clear()
            color_control.send_keys('1000')

        date_control = self.get_element_for_field('date')
        date_control.clear()
        date_control.send_keys("7/5/2015")

        self.click_save()

        block = self.load_root_xblock()  # Need to reload the block to bypass its cache

        self.assertEqual(block.color, '1000')
        self.assertEqual(block.count, 1000)
        self.assertEqual(block.comment, '1000')
        self.assertEqual(block.date, datetime.datetime(2015, 7, 5, 0, 0, 0, tzinfo=pytz.UTC))

        for field_name in EditableXBlock.editable_fields:
            self.click_reset_for_field(field_name)

        self.click_save()
        block = self.load_root_xblock()  # Need to reload the block to bypass its cache
        self.assert_unchanged(block)

    @XBlock.register_temp_plugin(EditableXBlock, "editable")
    def test_invalid_data(self):
        """
        Test that we get notified when there's a problem with our data.
        """
        def expect_error_message(expected_message):
            notification = self.dequeue_runtime_notification()
            self.assertEqual(notification[0], "error")
            self.assertEqual(notification[1]["title"], "Unable to update settings")
            self.assertEqual(notification[1]["message"], expected_message)

        block = self.set_up_root_block()

        color_control = self.get_element_for_field('color')
        color_control.clear()
        color_control.send_keys('orange')

        count_control = self.get_element_for_field('count')
        count_control.clear()
        count_control.send_keys('-10')

        comment_control = self.get_element_for_field('comment')
        comment_control.send_keys("That's a damn shame.")

        self.click_save(expect_success=False)
        expect_error_message("Count cannot be negative, No swearing allowed")
        self.assert_unchanged(self.load_root_xblock())

        count_control.clear()
        count_control.send_keys('10')

        self.click_save(expect_success=False)
        expect_error_message("No swearing allowed")
        self.assert_unchanged(self.load_root_xblock())

        comment_control.clear()

        self.click_save()


def fancy_list_values_provider_a(block):
    return [1, 2, 3, 4, 5]

def fancy_list_values_provider_b(block):
    return [{"display_name": "Robert", "value": "bob"}, {"display_name": "Alexandra", "value": "alex"}]


class FancyXBlock(StudioEditableXBlockMixin, XBlock):
    """
    A Studio-editable XBlock with lots of fields and fancy features
    """
    bool_normal = Boolean(display_name="Normal Boolean Field")
    dict_normal = Dict(display_name="Normal Dictionary Field")
    float_normal = Float(display_name="Normal Float Field")
    float_values = Float(display_name="Float Field With Values", values=(0, 2.718281, 3.14159,), default=0)
    int_normal = Integer(display_name="Normal Integer Field")
    int_ranged = Integer(display_name="Ranged Integer Field", values={"min": 0, "max": 10, "step": 2})
    int_dynamic = Integer(
        display_name="Integer Field With Dynamic Values",
        default=0,
        values=lambda: list(range(0, 10, 2))
    )
    int_values = Integer(
        display_name="Integer Field With Named Values",
        default=0,
        values=(
            {"display_name": "Yes", "value": 1},
            {"display_name": "No", "value": 0},
            {"display_name": "Maybe So", "value": -1},
        )
    )
    list_normal = List(display_name="Normal List")
    list_intdefs = List(display_name="Integer List With Default", default=[1, 2, 3, 4, 5])
    list_strdefs = List(display_name="String List With Default", default=['1', '2', '3', '4', '5'])

    list_set_ints = List(
        display_name="Int List (Set)",
        list_style="set",
        list_values_provider=fancy_list_values_provider_a,
        default=[1, 3, 5],
    )
    list_set_strings = List(
        display_name="String List (Set)",
        list_style="set",
        list_values_provider=fancy_list_values_provider_b,
        default=["alex"],
    )

    string_normal = String(display_name="Normal String Field")
    string_values = String(display_name="String Field With Values", default="A", values=("A", "B", "C", "D"))
    string_values_provider = String(
        display_name="String Field With Dynamic Values",
        default="",
        values_provider=lambda self: [unicode(self.scope_ids.usage_id), ""],
    )
    string_named = String(
        display_name="String Field With Named Values",
        default="AB",
        values=(
            {"display_name": "Alberta", "value": "AB"},
            {"display_name": "British Columbia", "value": "BC"},
        )
    )
    string_dynamic = String(
        display_name="String Field With Dynamic Values",
        default="",
        values=lambda: [""] + [letter for letter in "AEIOU"]
    )
    string_multiline = String(display_name="Multiline", multiline_editor=True, allow_reset=False)
    string_multiline_reset = String(display_name="Multiline", multiline_editor=True)
    string_html = String(display_name="Multiline", multiline_editor='html', allow_reset=False)
    string_with_help = String(
        display_name="String Field with Help Text",
        help="Learn more about <a class='field_help_link' href='https://en.wikipedia.org/wiki/Color'>colors</a>."
    )
    # Note: The HTML editor won't work in Workbench because it depends on Studio's TinyMCE

    editable_fields = (
        'bool_normal', 'dict_normal', 'float_normal', 'float_values', 'int_normal', 'int_ranged', 'int_dynamic',
        'int_values', 'list_normal', 'list_intdefs', 'list_strdefs', 'list_set_ints', 'list_set_strings',
        'string_normal', 'string_values', 'string_values_provider', 'string_named', 'string_dynamic',
        'string_multiline', 'string_multiline_reset', 'string_html', 'string_with_help'
    )

    def student_view(self, context):
        return Fragment()


class TestFancyXBlock_StudioView(StudioEditableBaseTest):
    """
    Test the Studio View created for FancyXBlock
    """

    def set_up_root_block(self):
        self.set_scenario_xml('<fancy />')
        self.go_to_view("studio_view")
        self.fix_js_environment()
        return self.load_root_xblock()

    @XBlock.register_temp_plugin(FancyXBlock, "fancy")
    def test_no_changes_with_defaults(self):
        """
        If we load the edit form and then save right away, there should be no changes.
        """
        block = self.set_up_root_block()
        orig_values = {field_name: getattr(block, field_name) for field_name in FancyXBlock.editable_fields}
        self.click_save()
        for field_name in FancyXBlock.editable_fields:
            self.assertEqual(getattr(block, field_name), orig_values[field_name])
            self.assertFalse(block.fields[field_name].is_set_on(block))

    @XBlock.register_temp_plugin(FancyXBlock, "fancy")
    def test_no_changes_with_values_set(self):
        """
        If the XBlock already has explicit values set, and we load the edit form and then save
        right away, there should be no changes.
        """
        block = self.set_up_root_block()
        block.bool_normal = True
        block.dict_normal = {"more": "cowbell"}
        block.float_normal = 17.0
        block.float_values = 3.14159
        block.int_normal = 10
        block.int_ranged = 8
        block.int_dynamic = 0
        block.int_values = -1
        block.list_normal = []
        block.list_intdefs = [9, 10, 11]
        block.list_strdefs = ['H', 'e', 'l', 'l', 'o']
        block.list_set_ints = [2, 3, 4]
        block.list_set_strings = ["bob"]
        block.string_normal = "A"
        block.string_values = "B"
        block.string_values_provider = unicode(block.scope_ids.usage_id)
        block.string_named = "BC"
        block.string_dynamic = "U"
        block.string_multiline = "why\nhello\there"
        block.string_multiline_reset = "indubitably"
        block.string_html = "<strong>Testing!</strong>"
        block.string_with_help = "Red"
        block.save()

        orig_values = {field_name: getattr(block, field_name) for field_name in FancyXBlock.editable_fields}
        # Reload the page:
        self.go_to_view("studio_view")
        self.fix_js_environment()

        self.click_save()
        block = self.load_root_xblock()  # Need to reload the block to bypass its cache
        for field_name in FancyXBlock.editable_fields:
            self.assertEqual(
                getattr(block, field_name),
                orig_values[field_name],
                "{} should be unchanged".format(field_name)
            )
            self.assertTrue(block.fields[field_name].is_set_on(block))

    @XBlock.register_temp_plugin(FancyXBlock, "fancy")
    def test_html_in_help(self):
        """
        If we include HTML in the help text for a field, the HTML should be displayed in the rendered page
        """
        block = self.set_up_root_block()
        try:
            self.browser.find_element_by_class_name('field_help_link')
        except NoSuchElementException:
            self.fail("HTML anchor tag missing from field help text")


class FancyBlockShim(object):
    CATEGORY = "fancy"
    STUDIO_LABEL = "Fancy Block"


class XBlockWithNested(StudioContainerWithNestedXBlocksMixin, XBlock):
    @property
    def allowed_nested_blocks(self):
        return [
            EditableXBlock,
            NestedXBlockSpec(FancyBlockShim, single_instance=True, boilerplate="fancy-boiler")
        ]


class XBlockWithDisabledNested(StudioContainerWithNestedXBlocksMixin, XBlock):
    @property
    def allowed_nested_blocks(self):
        return [
            NestedXBlockSpec(EditableXBlock, disabled=True, disabled_reason="Some reason"),
            NestedXBlockSpec(FancyBlockShim, disabled=False, disabled_reason="Irrelevant")
        ]


class XBlockWithOverriddenNested(StudioContainerWithNestedXBlocksMixin, XBlock):
    @property
    def allowed_nested_blocks(self):
        return [
            NestedXBlockSpec(UnawareXBlock, category='unaware', label='Unaware Block')
        ]


class StudioContainerWithNestedXBlocksTest(StudioContainerWithNestedXBlocksBaseTest):
    def setUp(self):
        super(StudioContainerWithNestedXBlocksTest, self).setUp()
        patcher = mock.patch(
            'workbench.runtime.WorkbenchRuntime.render_template', mock.Mock(side_effect=render_template)
        )
        patcher.start()

        self.addCleanup(patcher.stop)

    def _check_button(self, button, category, label, single, disabled, disabled_reason='', boilerplate=None):
        self.assertEqual(button.get_attribute('data-category'), category)
        self.assertEqual(button.text, label)
        self.assertEqual(button.get_attribute('data-single-instance'), str(single).lower())
        self._assert_disabled(button, disabled)
        self.assertEqual(button.get_attribute('title'), disabled_reason)
        self.assertEqual(button.get_attribute('data-boilerplate'), boilerplate)

    def _assert_disabled(self, button, disabled):
        if disabled:
            self.assertEqual(button.get_attribute('disabled'), 'true')
        else:
            self.assertEqual(button.get_attribute('disabled'), None)

    def set_up_root_block(self, scenario, view):
        self.set_scenario_xml(scenario)
        self.go_to_view(view)
        self.fix_js_environment()
        return self.load_root_xblock()

    @XBlock.register_temp_plugin(XBlockWithNested, "nested")
    def test_author_edit_view_nested(self):
        self.set_up_root_block("<nested />", "author_edit_view")

        add_buttons = self.get_add_buttons()
        self.assertEqual(len(add_buttons), 2)
        button_editable, button_fancy = add_buttons
        self._check_button(button_editable, EditableXBlock.CATEGORY, EditableXBlock.STUDIO_LABEL, False, False)
        self._check_button(
            button_fancy, FancyBlockShim.CATEGORY, FancyBlockShim.STUDIO_LABEL, True, False, boilerplate="fancy-boiler"
        )

    @XBlock.register_temp_plugin(XBlockWithDisabledNested, "nested")
    def test_author_edit_view_nested_with_disabled(self):
        self.set_up_root_block("<nested />", "author_edit_view")

        add_buttons = self.get_add_buttons()
        self.assertEqual(len(add_buttons), 2)
        button_editable, button_fancy = add_buttons
        self._check_button(
            button_editable, EditableXBlock.CATEGORY, EditableXBlock.STUDIO_LABEL, False, True, "Some reason"
        )
        self._check_button(button_fancy, FancyBlockShim.CATEGORY, FancyBlockShim.STUDIO_LABEL, False, False)

    @XBlock.register_temp_plugin(XBlockWithNested, "nested")
    def test_can_add_blocks(self):
        self.set_up_root_block("<nested />", "author_edit_view")
        button_editable, button_fancy = self.get_add_buttons()

        self._assert_disabled(button_editable, False)
        button_editable.click()
        self._assert_disabled(button_editable, False)
        button_editable.click()
        self._assert_disabled(button_editable, False)

        self._assert_disabled(button_fancy, False)
        button_fancy.click()
        self._assert_disabled(button_fancy, True)

    @XBlock.register_temp_plugin(XBlockWithNested, "nested")
    @XBlock.register_temp_plugin(FancyXBlock, "fancy")
    @XBlock.register_temp_plugin(EditableXBlock, "editable")
    def test_initial_state_with_blocks(self):
        scenario = textwrap.dedent("""
        <nested>
            <editable />
            <fancy />
        </nested>
        """)
        self.set_up_root_block(scenario, "author_edit_view")

        button_editable, button_fancy = self.get_add_buttons()
        self._assert_disabled(button_editable, False)
        self._assert_disabled(button_fancy, True)

    @XBlock.register_temp_plugin(XBlockWithOverriddenNested, "overrider")
    @XBlock.register_temp_plugin(UnawareXBlock, "unaware")
    def test_unaware_nested(self):
        scenario = textwrap.dedent("""
        <overrider />
        """)
        self.set_up_root_block(scenario, "author_edit_view")
        button_unaware = self.get_add_buttons()[0]
        self._assert_disabled(button_unaware, False)
        self.assertEqual(button_unaware.text, 'Unaware Block')
