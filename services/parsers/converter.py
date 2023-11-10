from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from .parsers import parse_excel

FILE_FORMAT_HANDLERS = {
    'xls': parse_excel,
    'xlsx': parse_excel,
}


def convert_file_to_data(file):
    ext = file.name.strip().split('.')[-1]
    if not FILE_FORMAT_HANDLERS.get(ext):
        raise ValidationError({'message': _('This format is not supported.')})

    return FILE_FORMAT_HANDLERS[ext](file)
