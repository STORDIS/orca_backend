from grpc import RpcError
from rest_framework.request import Request


def get_failure_msg(err: Exception, request: Request, req_data: dict):
    """
    Generate a message for a failed request.

    Args:
        err (Exception): The exception that was raised.
        request (Request): The request object.
        req_data (dict): The data associated with the request.

    Returns:
        str: The error message.
    """
    return f"{request.method} request failed : {req_data} Reason: {err.details() if isinstance(err, RpcError) else str(err)}"


def get_success_msg(request: Request, req_data: dict):
    """
    Generate a message for a successful request.

    Args:
        request (Request): The request object.
        req_data (dict): The data associated with the request.

    Returns:
        str: The success message.
    """
    return f"{request.method} request successful : {req_data}"


def add_msg_to_list(msg_list: [], msg):
    """
    Add a message to a list of messages.

    Args:
        msg_list (list): The list of messages.
        msg (str): The message to add.
    """
    if msg_list:
        msg_list.append("\n")
    msg_list.append(msg)
    return msg_list
