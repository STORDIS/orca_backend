import datetime
import time
from log_manager.serializers import LogSerializer


def log(func):
    def wrapper(request):
        data = {
            "timestamp": str(datetime.datetime.now(tz=datetime.timezone.utc)),
            "request_json": request.data,
            "status": "processing",
            "processing_time": "0"
        }
        start_time = time.time()
        serializer = LogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        resp = func(request)
        if resp.status_code >= 400:
            data["status"] = "failed"
        else:
            data["status"] = "success"
        data["processing_time"] = time.time() - start_time
        serializer = LogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        return resp
    return wrapper

