import datetime
import json
import traceback

from django.core.paginator import Paginator, EmptyPage
from django_celery_results.models import TaskResult
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from log_manager.models import Logs


# Create your views here.

@api_view(['get'])
def get_logs(request: Request, **kwargs):
    """
    function to get logs save logs

    Parameters:
    - request: The Django request object.

    Returns:
    - If successful, returns a JSON response with logs list and 200 ok status.
    - If fails returns a JSON response with 500 status.
    """
    try:
        final_result = []
        query_params = request.query_params
        items = Logs.objects.all().order_by("-timestamp")
        paginator = Paginator(items, query_params.get("size", 10))  # sizeof return list
        logs_result = paginator.page(kwargs["page"])  # page no
        final_result.extend(logs_result.object_list.values())
        final_result.extend(get_celery_tasks_data())
        final_result.sort(
            key=lambda x: datetime.datetime.strptime(
                x["timestamp"], "%Y-%m-%d %H:%M:%S"
            ),
            reverse=True
        )
        return Response(final_result, status=status.HTTP_200_OK)
    except EmptyPage as e:
        print(str(e))
        return Response({"message": str(e)}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['delete'])
def delete_logs(request: Request, **kwargs):
    """
    function to delete all logs

    Parameters:
    - request: The Django request object.

    Returns:
    - If successful, returns a JSON response with logs list and 200 ok status.
    - If fails returns a JSON response with 500 status.
    """
    try:
        Logs.objects.all().delete()
        return Response({"message": "deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_celery_tasks_data():
    task_results = TaskResult.objects.all()
    result_data = []
    for result in task_results:
        responses = json.loads(result.result) if result.result else {}
        result_data.append(
            {
                "status": result.status,
                "timestamp": result.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                "status_code": 200,
                "http_method": "PUT",
                "processing_time": (result.date_done - result.date_created).total_seconds(),
                "response": responses.get("result", None),
                "request_json": responses.get("request_data", None),
                "http_path": responses.get("http_path", None),
                "task_id": result.task_id
            }
        )
    return result_data
