from xblock.core import XBlock


class PublishEventMixin(object):
    """A mixin for publishing events from an XBlock

    Reuqires the object to have a runtime.publish method.
    """
    additional_publish_event_data = {}

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):
        try:
            event_type = data.pop('event_type')
        except KeyError as e:
            return {'result': 'error', 'message': 'Missing event_type in JSON data'}

        return self.publish_event_from_python(event_type, data)

    def publish_event_from_python(self, event_type, data):
        for key, value in self.additional_publish_event_data.items():
            if key in data:
                return {'result': 'error', 'message': 'Key should not be in publish_event data: {}'.format(key)}
            data[key] = value

        self.runtime.publish(self, event_type, data)
        return {'result': 'success'}
