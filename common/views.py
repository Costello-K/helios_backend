from rest_framework import status
from rest_framework.response import Response


def get_serializer_paginate(instance, queryset, serializer):
    page = instance.paginate_queryset(queryset=queryset)
    if page is not None:
        serializer = serializer(page, many=True)
        return instance.get_paginated_response(data=serializer.data)

    serializer = serializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
