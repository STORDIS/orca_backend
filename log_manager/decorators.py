import datetime
import time
from functools import wraps

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
                "status_code": response.status_code
            }
            response_data = response.data
            if "result" in response_data:
                responses = create_request_response_data(request_data=request.data, response_data=response_data["result"])
            else:
                responses = create_request_response_data(request_data=request.data, response_data=response_data)
            for i in responses:
                if "status" not in i:
                    if response.status_code >= 400:
                        i["status"] = "failed"
                    else:
                        i["status"] = "success"
                serializer = LogSerializer(data={**data, **i, "http_method": request.method})
                if serializer.is_valid():
                    serializer.save()
            return response
        else:
            return function(request, *args, **kwargs)
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
            {"response": response_data, "request_json": request_data}
        ]
