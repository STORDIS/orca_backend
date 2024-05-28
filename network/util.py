from grpc import RpcError
from rest_framework.request import Request


def get_failure_msg(err: Exception, request: Request):
    """
    Generate a message for a failed request.

    Args:
        err (Exception): The exception that was raised.
        request (Request): The request object.

    Returns:
        dict: The failure message with the error details and status.
    """
    message = f"{request.method} request failed, Reason: {err.details() if isinstance(err, RpcError) else str(err)}"
    return {"status": "failed", "message": message}


def get_success_msg(request: Request):
    """
    Generate a message for a successful request.

    Args:
        request (Request): The request object.

    Returns:
        dict: The success message and status.
    """
    message = f"{request.method} request successful"
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
