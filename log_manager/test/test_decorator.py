import json

from rest_framework import permissions
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework.test import APITestCase, APIRequestFactory

from log_manager.decorators import log_request
from log_manager.test.test_common import TestCommon


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@log_request
def stub1(request):
    return Response({"result": "testing"}, status=200)


@api_view(["GET", "POST"])
@permission_classes([permissions.AllowAny])
@log_request
def stub2(request):
    return Response({"result": ["test_1", "test_2", "test_3"]}, status=200)


class TestDecorator(TestCommon):

    def test_decorator_1(self):
        self.request = self.factory.post("/stub/path", format="json")
        response = stub1(self.request)
        assert response.status_code == 200
        get_response = self.client.get(
            path="/logs/all/1",
            HTTP_AUTHORIZATION=self.tkn
        )
        print(get_response.data)
        for i in get_response.data:
            assert i["response"] == "testing"
        assert get_response.data[0]["status_code"] == response.status_code

    def test_decorator_2(self):
        self.request = self.factory.get("/stub/path", format="json")
        response = stub2(self.request)
        assert response.status_code == 200
        get_response = self.client.get(
            path="/logs/all/1",
            HTTP_AUTHORIZATION=self.tkn
        )
        assert get_response.status_code == 200
        for i in get_response.data:
            assert i["response"] in ["test_1", "test_2", "test_3"]

    def test_decorator_3(self):
        self.request = self.factory.post(
            "/stub/path",
            data=[{'key_1': "value_1"}, {'key_2': "value_2"}, {'key_3': "value_3"}],
            format="json"
        )
        response = stub2(self.request)
        assert response.status_code == 200
        get_response = self.client.get(
            path="/logs/all/1",
            HTTP_AUTHORIZATION=self.tkn
        )
        for i in get_response.data:
            assert i["response"] in ["test_1", "test_2", "test_3"]
            assert i["request_json"] in [{'key_1': "value_1"}, {'key_2': "value_2"}, {'key_3': "value_3"}]

    def test_decorator_ignore_get_request(self):
        self.request = self.factory.get("/stub/path", format="json")
        response = stub2(self.request)
        assert response.status_code == 200
        get_response = self.client.get(
            path="/logs/all/1",
            HTTP_AUTHORIZATION=self.tkn
        )
        print(get_response.data)
        assert get_response.status_code == 200
        assert len(get_response.data) == 0
