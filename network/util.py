import datetime
import time
import uuid
from typing import Union

from grpc import RpcError
from rest_framework.request import Request

from log_manager.models import Logs
from log_manager.serializers import LogSerializer
from orca_backend.celery import get_queue_length


def get_failure_msg(err: Exception, method):
    """
    Generate a message for a failed request.

    Args:
        err (Exception): The exception that was raised.
        request (Request): The request object.

    Returns:
        dict: The failure message with the error details and status.
    """
    message = f"{method} request failed, Reason: {err.details() if isinstance(err, RpcError) else str(err)}"
    return {"status": "failed", "message": message}


def get_success_msg(method):
    """
    Generate a message for a successful request.

    Args:
        request (Request): The request object.

    Returns:
        dict: The success message and status.
    """
    message = f"{method} request successful"
    return {"status": "success", "message": message}


def add_msg_to_list(msg_list: [], msg):
    """
    Add a message to a list of messages.

    Args:
        msg_list (list): The list of messages.
        msg (dict): The message to add.
    """
    if msg_list:
        msg_list.append("\n")
    msg_list.append(msg)
    return msg_list


def save_log(request_data: Union[dict | list], method: str):
    """
    Save the log data to the database.

    Args:
        request_data (dict | list): The request data.
        method (str): The HTTP method.
    """
    q_len = get_queue_length("celery")
    if q_len > 20:
        raise Exception("Queue is full. Please try again later.")
    task_id = uuid.uuid4().hex
    data = {
        "timestamp": str(datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
        "processing_time": 0,
        "status_code": 200,
        "http_method": method,
        "request_json": request_data,
        "response": "",
        "status": "Pending",
        "task_id": task_id
    }
    serializer = LogSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
    return task_id
