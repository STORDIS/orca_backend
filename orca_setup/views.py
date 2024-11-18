import ast
import json

from django_celery_results.models import TaskResult
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from log_manager.logger import get_backend_logger
from orca_backend.celery import cancel_task

_logger = get_backend_logger()


@api_view(["GET", "DELETE"])
def celery_task(request):
    """
    This function is an API view that handles the HTTP DELETE requests for the 'cancel_celery_task' endpoint.
    """
    result = []
    if request.method == "GET":
        task_id = request.GET.get("task_id", None)
        if task_id:
            data = _modify_celery_results(TaskResult.objects.get_task(task_id=task_id))
        else:
            data = [_modify_celery_results(i) for i in TaskResult.objects.all()]
        return (
            Response(data, status=status.HTTP_200_OK)
            if data
            else Response({}, status=status.HTTP_204_NO_CONTENT)
        )
    if request.method == "DELETE":
        req_data_list = (
            request.data if isinstance(request.data, list) else [request.data]
        )
        for req_data in req_data_list:
            task_id = req_data.get("task_id", None)
            if not task_id:
                _logger.error("Required field device task_id not found.")
                return Response(
                    {"result": "Required field device task_id not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                _logger.info(f"canceling task {task_id}")
                cancel_task(task_id)
                result.append({
                    "message": f"{request.method}: {task_id} canceled",
                    "status": "success"
                })
            except Exception as e:
                _logger.error(e)
                result.append({
                    "message": f"{request.method}: {task_id} failed with error: {e}",
                    "status": "failed"
                })
        return Response({"result": result}, status=status.HTTP_200_OK)


def _modify_celery_results(result):
    try:
        task_kwargs = ast.literal_eval(result.task_kwargs.strip('\"')) if result.task_kwargs else {}
    except:
        task_kwargs = result.task_kwargs
    http_path = task_kwargs.pop("http_path", "")
    return {
        "status": result.status,
        "timestamp": result.date_created.strftime("%Y-%m-%d %H:%M:%S"),
        "status_code": 200,
        "http_method": "PUT",
        "processing_time": (result.date_done - result.date_created).total_seconds(),
        "response": json.loads(result.result),
        "request_json": task_kwargs,
        "http_path": http_path,
        "task_id": result.task_id,
    }
