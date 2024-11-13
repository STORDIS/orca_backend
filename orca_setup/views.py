from django.forms import model_to_dict
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
            data = model_to_dict(TaskResult.objects.get_task(task_id=task_id))
        else:
            data = TaskResult.objects.all().values()
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
