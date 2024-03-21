from rest_framework import serializers
from log_manager.models import Logs


class LogSerializer(serializers.ModelSerializer):
    """
    Log serializer to save logs data
    """
    class Meta:
        model = Logs
        fields = (
            'timestamp', 'request_json', "status", "processing_time",
            "response", "status_code", "http_method"
        )
        extra_kwargs = {
            'timestamp': {'required': True},
            'request_json': {'required': True},
            "status": {'required': True},
            "processing_time": {'required': True},
            "response": {'required': True},
            "status_code": {'required': True},
            "http_method": {'required': True}
        }

    def save(self, **kwargs):
        """
        This function save and updates logs based on time stamp and requested data.
        """
        super().save()
        self._read_adjust_rows_length()  # resets rows count to 1000
        return self

    def _read_adjust_rows_length(self):
        """
        function to delete first row if greater than 1000
        """
        items = Logs.objects.all()
        if items.count() > 1000:
            items.first().delete()  # deleting first row
        return self
