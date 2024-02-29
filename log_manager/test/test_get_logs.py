from log_manager.serializers import LogSerializer
from rest_framework.test import APITestCase


class TestGetLogs(APITestCase):

    def test_get_logs(self):
        data = {
            "timestamp": "timestamp",
            "request_json": {
                "key": "value"
            },
            "processing_time": 0,
            "status": "success"
        }
        serializer = LogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        response = self.client.get(
            "/logs/1?size=1000",
        )
        assert any([i["timestamp"] == "timestamp" for i in response.json()])

    def test_get_paginated_logs(self):
        for i in range(3):
            serializer = LogSerializer(
                data={
                    "timestamp": f"timestamp_{i}",
                    "request_json": {
                        "key": "value"
                    },
                    "processing_time": 0,
                    "status": "success"
                }
            )
            if serializer.is_valid():
                serializer.save()
        response = self.client.get(
            f"/logs/1?size=5",
        )
        response_json = response.json()
        assert response.status_code == 200
        assert 3 <= len(response_json) <= 5



