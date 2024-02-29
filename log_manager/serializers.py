from django.contrib.auth.models import User, Group
from oauth2_provider.contrib.rest_framework import TokenHasScope, TokenHasReadWriteScope
from rest_framework import serializers, generics, permissions

from log_manager.models import Logs


class LogSerializer(serializers.ModelSerializer):
    """
    Log serializer to save logs data
    """
    class Meta:
        model = Logs
        fields = ('timestamp', 'request_json', "status", "processing_time")

    def save(self, **kwargs):
        """
        This function save and updates logs based on time stamp and requested data.
        """
        timestamp = self.validated_data["timestamp"]
        request_json = self.validated_data["request_json"]
        items = Logs.objects.filter(timestamp=timestamp, request_json=request_json)
        if items.count() > 0:
            items.update(**self.validated_data)
        else:
            super().save()  # saves logs
        self._read_adjust_rows_length()  # resets rows count to 1000
        return self

    def _read_adjust_rows_length(self):
        items = Logs.objects.all()
        if items.count() > 1000:
            items.first().delete()
        return self
