from django.conf import settings


class AddAccessControlAllowOriginCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method == 'OPTIONS' and 'HTTP_ACCESS_CONTROL_REQUEST_HEADERS' in request.META:
            response['Access-Control-Allow-Headers'] = request.META['HTTP_ACCESS_CONTROL_REQUEST_HEADERS']

        response['Access-Control-Allow-Origin'] = f'https://{settings.ALLOWED_HOSTS[0]}'
        response['Access-Control-Allow-Methods'] = '*'
        response['Access-Control-Allow-Credentials'] = 'true'

        return response
