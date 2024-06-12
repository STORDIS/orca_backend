from log_manager.serializers import LogSerializer

from log_manager.test.test_common import TestCommon


class TestGetLogs(TestCommon):

    def test_get_logs(self):
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
            "status_code": 200,
            "task_id": "task_id"
        }
        serializer = LogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        response = self.client.get(
            "/logs/all/1?size=1000",
            HTTP_AUTHORIZATION=self.tkn
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
                    "status": "success",
                    "response": {
                        "key": "value"
                    },
                    "http_method": "POST",
                    "status_code": 200,
                    "task_id": "task_id"
                }
            )
            if serializer.is_valid():
                serializer.save()
        response = self.client.get(
            f"/logs/all/1?size=5",
            HTTP_AUTHORIZATION=self.tkn
        )
        response_json = response.json()
        assert response.status_code == 200
        assert 3 <= len(response_json) <= 5



