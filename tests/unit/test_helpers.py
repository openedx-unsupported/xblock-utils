"""
Tests for helpers.py
"""
from __future__ import absolute_import
import unittest
from workbench.runtime import WorkbenchRuntime
from xblock.core import XBlock
from xblockutils.helpers import child_isinstance


class DogXBlock(XBlock):
    """ Test XBlock representing any dog. Raises error if instantiated. """
    pass


class GoldenRetrieverXBlock(DogXBlock):
    """ Test XBlock representing a golden retriever """
    pass


class CatXBlock(XBlock):
    """ Test XBlock representing any cat """
    pass


class BasicXBlock(XBlock):
    """ Basic XBlock """
    has_children = True


class TestChildIsInstance(unittest.TestCase):
    """
    Test child_isinstance helper method, in the workbench runtime.
    """

    @XBlock.register_temp_plugin(GoldenRetrieverXBlock, "gr")
    @XBlock.register_temp_plugin(CatXBlock, "cat")
    @XBlock.register_temp_plugin(BasicXBlock, "block")
    def test_child_isinstance(self):
        """
        Check that child_isinstance() works on direct children
        """
        self.runtime = WorkbenchRuntime()
        self.root_id = self.runtime.parse_xml_string('<block> <block><cat/><gr/></block> <cat/> <gr/> </block>')
        root = self.runtime.get_block(self.root_id)
        self.assertFalse(child_isinstance(root, root.children[0], DogXBlock))
        self.assertFalse(child_isinstance(root, root.children[0], GoldenRetrieverXBlock))
        self.assertTrue(child_isinstance(root, root.children[0], BasicXBlock))

        self.assertFalse(child_isinstance(root, root.children[1], DogXBlock))
        self.assertFalse(child_isinstance(root, root.children[1], GoldenRetrieverXBlock))
        self.assertTrue(child_isinstance(root, root.children[1], CatXBlock))

        self.assertFalse(child_isinstance(root, root.children[2], CatXBlock))
        self.assertTrue(child_isinstance(root, root.children[2], DogXBlock))
        self.assertTrue(child_isinstance(root, root.children[2], GoldenRetrieverXBlock))

    @XBlock.register_temp_plugin(GoldenRetrieverXBlock, "gr")
    @XBlock.register_temp_plugin(CatXBlock, "cat")
    @XBlock.register_temp_plugin(BasicXBlock, "block")
    def test_child_isinstance_descendants(self):
        """
        Check that child_isinstance() works on deeper descendants
        """
        self.runtime = WorkbenchRuntime()
        self.root_id = self.runtime.parse_xml_string('<block> <block><cat/><gr/></block> <cat/> <gr/> </block>')
        root = self.runtime.get_block(self.root_id)
        block = root.runtime.get_block(root.children[0])
        self.assertIsInstance(block, BasicXBlock)

        self.assertFalse(child_isinstance(root, block.children[0], DogXBlock))
        self.assertTrue(child_isinstance(root, block.children[0], CatXBlock))

        self.assertTrue(child_isinstance(root, block.children[1], DogXBlock))
        self.assertTrue(child_isinstance(root, block.children[1], GoldenRetrieverXBlock))
        self.assertFalse(child_isinstance(root, block.children[1], CatXBlock))
