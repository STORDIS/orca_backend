from rest_framework.decorators import api_view
from rest_framework.response import Response

from orcask.model import completions

# Create your views here.


@api_view(["POST"])
def completions_view(request):
    try:
        data = request.data
        response = completions.ask_gpt(data=data)
        return Response(status=200, data=response)
    except Exception as e:
        return Response(status=200, data={"message": str(e)})
