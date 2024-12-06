import ast
import datetime
import json

from celery import states
from django.core.paginator import Paginator, EmptyPage
from django_celery_results.models import TaskResult
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from log_manager.logger import get_backend_logger
from log_manager.models import Logs
from orca_backend.celery import cancel_task

_logger = get_backend_logger()


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
        final_result.extend(logs_result.object_list.values())  # add logs
        final_result.extend(get_celery_tasks_data())  # add celery task data

        # sort by timestamp
        final_result.sort(
            key=lambda x: datetime.datetime.strptime(
                x["timestamp"], "%Y-%m-%d %H:%M:%S"
            ),
            reverse=True
        )
        return Response(final_result, status=status.HTTP_200_OK)
    except EmptyPage as e:
        _logger.error("EmptyPage Error: ", e)
        return Response({"message": str(e)}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        _logger.error("Error: ", e)
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
        data = request.data
        log_ids = data.get("log_ids", [])
        task_ids = data.get("task_ids", [])

        if log_ids:
            _logger.debug("Deleting logs for given ids: %s", log_ids)
            Logs.objects.filter(id__in=log_ids).delete()
        if task_ids:
            _logger.debug("Deleting celery tasks: %s", task_ids)
            delete_celery_tasks_data(task_ids)

        if not log_ids and not task_ids:
            _logger.info("Deleting all logs")
            Logs.objects.all().delete()
            delete_celery_tasks_data()
        return Response({"message": "deleted successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        _logger.error("Error: ", e)
        return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_celery_tasks_data() -> list:
    """
    function to get celery tasks data from database

    Returns:
        - list: celery tasks data
    """
    task_results = TaskResult.objects.all()
    result_data = []
    for result in task_results:
        try:
            task_kwargs = ast.literal_eval(result.task_kwargs.strip('\"')) if result.task_kwargs else {}
        except ValueError:
            task_kwargs = {"result": result.task_kwargs}
        http_path = task_kwargs.pop("http_path", "")
        result_data.append(
            {
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
        )
    return result_data


def delete_celery_tasks_data(task_ids: list = None) -> None:
    """
    function to delete celery tasks data from database

    Parameters:
        - task_ids: list of task ids
    Returns:
        - None
    """
    tasks = TaskResult.objects.exclude(status=states.STARTED)
    if task_ids:
        tasks = tasks.filter(task_id__in=task_ids)
    for i in tasks:
        # cancel task if not started
        if i.status == states.PENDING:
            cancel_task(i.task_id)

    # delete all task
    tasks.delete()
