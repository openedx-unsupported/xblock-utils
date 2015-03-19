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
PublishEventMixin: A mixin for publishing events from an XBlock
"""

from xblock.core import XBlock


class PublishEventMixin(object):
    """
    A mixin for publishing events from an XBlock

    Requires the object to have a runtime.publish method.
    """
    additional_publish_event_data = {}

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):
        """
        AJAX handler to allow client-side code to publish a server-side event
        """
        try:
            event_type = data.pop('event_type')
        except KeyError:
            return {'result': 'error', 'message': 'Missing event_type in JSON data'}

        return self.publish_event_from_dict(event_type, data)

    def publish_event_from_dict(self, event_type, data):
        """
        Combine 'data' with self.additional_publish_event_data and publish an event
        """
        for key, value in self.additional_publish_event_data.items():
            if key in data:
                return {'result': 'error', 'message': 'Key should not be in publish_event data: {}'.format(key)}
            data[key] = value

        self.runtime.publish(self, event_type, data)
        return {'result': 'success'}
