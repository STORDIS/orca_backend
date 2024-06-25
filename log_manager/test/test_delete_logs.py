from log_manager.serializers import LogSerializer
from log_manager.test.test_common import TestCommon


class TestDeleteLogs(TestCommon):

    def test_delete_logs(self):
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
        response = self.client.get(
            "/logs/all/1?size=1000",
            HTTP_AUTHORIZATION=self.tkn
        )
        assert response.status_code == 200
        assert any([i["timestamp"] == "timestamp" for i in response.json()])
        self.client.delete("/logs/delete", HTTP_AUTHORIZATION=self.tkn)
        response_after_delete = self.client.get(
            "/logs/all/1?size=1000",
            HTTP_AUTHORIZATION=self.tkn
        )
        assert response_after_delete.status_code == 200
        assert len(response_after_delete.json()) == 0
