from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from .converters import data_to_csv, data_to_json

FILE_FORMAT_HANDLERS = {
    'json': data_to_json,
    'csv': data_to_csv,
}


def convert_data_to_file(data, format_file):
    if not FILE_FORMAT_HANDLERS.get(format_file):
        raise ValidationError({'message': _('This format is not supported.')})

    return FILE_FORMAT_HANDLERS[format_file](data)
