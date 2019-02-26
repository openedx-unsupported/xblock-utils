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

from __future__ import absolute_import
import unittest
import json

from xblockutils.publish_event import PublishEventMixin


class EmptyMock():
    pass


class RequestMock(object):
    method = "POST"

    def __init__(self, data):
        self.body = json.dumps(data)


class RuntimeMock(object):
    last_call = None

    def publish(self, block, event_type, data):
        self.last_call = (block, event_type, data)


class XBlockMock(object):
    def __init__(self):
        self.runtime = RuntimeMock()


class ObjectUnderTest(XBlockMock, PublishEventMixin):
    pass


class TestPublishEventMixin(unittest.TestCase):
    def assert_no_calls_made(self, block):
        self.assertFalse(block.last_call)

    def assert_success(self, response):
        self.assertEquals(json.loads(response.body)['result'], 'success')

    def assert_error(self, response):
        self.assertEquals(json.loads(response.body)['result'], 'error')

    def test_error_when_no_event_type(self):
        block = ObjectUnderTest()

        response = block.publish_event(RequestMock({}))

        self.assert_error(response)
        self.assert_no_calls_made(block.runtime)

    def test_uncustomized_publish_event(self):
        block = ObjectUnderTest()

        event_data = {"one": 1, "two": 2, "bool": True}
        data = dict(event_data)
        data["event_type"] = "test.event.uncustomized"

        response = block.publish_event(RequestMock(data))

        self.assert_success(response)
        self.assertEquals(block.runtime.last_call, (block, "test.event.uncustomized", event_data))

    def test_publish_event_with_additional_data(self):
        block = ObjectUnderTest()
        block.additional_publish_event_data = {"always_present": True, "block_id": "the-block-id"}

        event_data = {"foo": True, "bar": False, "baz": None}
        data = dict(event_data)
        data["event_type"] = "test.event.customized"

        response = block.publish_event(RequestMock(data))

        expected_data = dict(event_data)
        expected_data.update(block.additional_publish_event_data)

        self.assert_success(response)
        self.assertEquals(block.runtime.last_call, (block, "test.event.customized", expected_data))

    def test_publish_event_fails_with_duplicate_data(self):
        block = ObjectUnderTest()
        block.additional_publish_event_data = {"good_argument": True, "clashing_argument": True}

        event_data = {"fine_argument": True, "clashing_argument": False}
        data = dict(event_data)
        data["event_type"] = "test.event.clashing"

        response = block.publish_event(RequestMock(data))

        self.assert_error(response)
        self.assert_no_calls_made(block.runtime)
