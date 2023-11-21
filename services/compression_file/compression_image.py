from io import BytesIO

from django.utils.translation import gettext_lazy as _
from PIL import Image
from rest_framework.exceptions import ValidationError


def compress_image_to_given_resolution(file, max_resolution):
    if not hasattr(file, 'size'):
        raise ValidationError({'message': _('An invalid object was passed. A file was expected.')})
    try:
        compression_image = Image.open(BytesIO(file.read()))
        compression_image.thumbnail((max_resolution, max_resolution))
        output = BytesIO()
        compression_image.save(output, format=compression_image.format)
        return output.getvalue()
    except Exception as err:
        return ValidationError({'message': err})
