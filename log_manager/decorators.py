import datetime
import time
from functools import wraps

from log_manager.models import Logs
from log_manager.serializers import LogSerializer


def log_request(function):
    """
    Decorator function to add data.
    """

    @wraps(function)
    def _wrapper(request, *args, **kwargs):
        if request.method != "GET":
            start = time.time()
            response = function(request, *args, **kwargs)
            data = {
                "timestamp": str(datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
                "processing_time": time.time() - start,
                "status_code": response.status_code,
                "task_id": response.data["task_id"] if "task_id" in response.data else "default",
            }
            # if response.status_code >= 400:
            #     data["status"] = "failed"
            # else:
            #     data["status"] = "success"
            response_data = response.data
            if "result" in response_data:
                responses = create_request_response_data(request_data=request.data,
                                                         response_data=response_data["result"])
            else:
                responses = create_request_response_data(request_data=request.data, response_data=response_data)
            for i in responses:
                print({**data, **i, "http_method": request.method})
                serializer = LogSerializer(data={**data, **i, "http_method": request.method})
                print(
                    "------------", serializer.is_valid(), serializer.errors, "------------"
                )
                if serializer.is_valid():
                    serializer.save()
            return response
        else:
            return function(request, *args, **kwargs)

    return _wrapper


def log_task(function):
    """
    Decorator function to add data.
    """

    @wraps(function)
    def _wrapper(request_list, method, task_id=None, *args, **kwargs):
        if method != "GET":
            start = time.time()
            response = function(request_list, method, task_id, *args, **kwargs)
            response_result = response.data
            if task_id is None:
                task_id = response["task_id"]
            data = {
                "timestamp": str(datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
                "processing_time": time.time() - start,
                "status_code": response.get("status", 200)
            }
            if "result" in response_result:
                responses = create_request_response_data(request_data=request_list,
                                                         response_data=response_result["result"])
            else:
                responses = create_request_response_data(request_data=request_list, response_data=response_result)
            Logs.objects.filter(task_id=task_id).delete()
            for i in responses:
                serializer = LogSerializer(
                    data={**data, **i, "http_method": method, "task_id": task_id}
                )
                if serializer.is_valid():
                    serializer.save()
            return response.data
        else:
            response = function(request_list, method, *args, **kwargs)
            return response.data

    return _wrapper


def create_request_response_data(request_data, response_data):
    if isinstance(response_data, list):
        response_data = [i for i in response_data if i != "\n" and i]
        if isinstance(request_data, list) and len(response_data) == len(request_data):
            return [
                {
                    "response": response_data[i]["message"],
                    "status": response_data[i]["status"],
                    "request_json": request_data[i]
                } for i in range(len(response_data))
            ]
        else:
            return [
                {
                    "response": response_data[i]["message"],
                    "status": response_data[i]["status"],
                    "request_json": request_data
                } for i in range(len(response_data))
            ]
    else:
        return [
            {
                "response": response_data["message"] if 'message' in response_data else response_data,
                "request_json": request_data,
                "status": response_data["status"]
            }
        ]
