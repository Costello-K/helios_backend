from rest_framework import status
from rest_framework.response import Response

from services.export.response_builder import convert_data_to_file


def get_serializer_paginate(instance, queryset, serializer, context=None):
    page = instance.paginate_queryset(queryset=queryset)
    if page is not None:
        serializer = serializer(page, many=True, context=context)
        return instance.get_paginated_response(data=serializer.data)

    serializer = serializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def get_user_quiz_result_response(instance, request, queryset, context=None):
    export_format = request.query_params.get('export_format')
    if export_format:
        serializer = instance.get_serializer(queryset, many=True, context=context)
        return convert_data_to_file(data=serializer.data, format_file=export_format)

    return get_serializer_paginate(instance, queryset, instance.get_serializer, context=context)
