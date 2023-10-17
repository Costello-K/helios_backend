from rest_framework.exceptions import APIException


class CustomBaseException(APIException):
    default_detail = ''

    def __init__(self, detail=default_detail):
        self.detail = detail


class ObjectAlreadyInInstance(CustomBaseException):
    status_code = 400
    default_detail = 'Object is already in instance.'


class ObjectNotInInstance(CustomBaseException):
    status_code = 400
    default_detail = 'Object is not in the instance.'


class ObjectNotHavePermissions(CustomBaseException):
    status_code = 400
    default_detail = 'The object does not have permissions.'


class ObjectDoesNotExist(CustomBaseException):
    status_code = 404
    default_detail = 'Object does not exist.'
