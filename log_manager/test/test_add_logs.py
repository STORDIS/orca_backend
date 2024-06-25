from rest_framework.generics import get_object_or_404
from log_manager.models import Logs
from log_manager.serializers import LogSerializer
from log_manager.test.test_common import TestCommon


class TestAddLogs(TestCommon):

    def test_add_logs(self):
        data = {
            "timestamp": "timestamp",
            "request_json": {
                "key": "value"
            },
            "processing_time": 0,
            "status": "success",
            "response": {
                "key": "value"
            },
            "http_method": "POST",
            "status_code": 200
        }
        serializer = LogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        logs = get_object_or_404(Logs.objects.filter(timestamp=data["timestamp"]))
        assert logs.request_json == data["request_json"]

    def test_update_logs(self):
        data = {
            "timestamp": "timestamp",
            "request_json": {
                "key": "value"
            },
            "processing_time": 0,
            "status": "processing",
            "response": {
                "key": "value"
            },
            "http_method": "POST",
            "status_code": 200
        }
        serializer = LogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        filter_result_1 = Logs.objects.filter(timestamp=data["timestamp"])
        logs_1 = get_object_or_404(filter_result_1)
        assert logs_1.request_json == data["request_json"]
        assert logs_1.status == "processing"
        data["status"] = "failure"
        data["processing_time"] = 10
        data["timestamp"] = "timestamp_1"
        serializer = LogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        filter_result_2 = Logs.objects.filter(timestamp=data["timestamp"])
        logs_2 = get_object_or_404(filter_result_2)
        assert logs_2.status == "failure"
        assert logs_2.processing_time == '10'
        data["status"] = "success"
        data["processing_time"] = '15'
        data["timestamp"] = "timestamp_2"
        serializer = LogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        filter_result_3 = Logs.objects.filter(timestamp=data["timestamp"])
        logs_3 = get_object_or_404(filter_result_3)
        assert logs_3.status == "success"
        assert logs_3.processing_time == '15'
