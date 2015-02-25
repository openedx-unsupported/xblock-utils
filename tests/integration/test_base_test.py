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
