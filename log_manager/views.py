import traceback

from django.core.paginator import Paginator, EmptyPage
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
        query_params = request.query_params
        items = Logs.objects.all().order_by("-timestamp")
        paginator = Paginator(items, query_params.get("size", 10))  # sizeof return list
        result = paginator.page(kwargs["page"])  # page no
        return Response(result.object_list.values(), status=status.HTTP_200_OK)
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
