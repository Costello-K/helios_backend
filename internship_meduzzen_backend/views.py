from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def server_check(request):
    return Response({
        'status_code': status.HTTP_200_OK,
        'detail': 'ok',
        'result': 'working',
    })
