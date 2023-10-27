from .converters import data_to_csv, data_to_json

FILE_FORMAT_HANDLERS = {
    'json': data_to_json,
    'csv': data_to_csv,
}


def convert_data_to_file(data, format_file):
    return FILE_FORMAT_HANDLERS[format_file](data)
