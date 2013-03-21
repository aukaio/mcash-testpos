from django.core.serializers import json


class Serializer(json.Serializer):
    def get_dump_object(self, obj):
        self._current['id'] = obj.pk
        self._current['image_url'] = obj.image_url
        return self._current

