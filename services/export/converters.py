import csv
import json
import tempfile
from decimal import Decimal

from django.http import HttpResponse


def create_response(file, format_file, content_type):
    with open(file.name, 'rb') as file_data:
        response = HttpResponse(file_data.read(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="quiz_results.{format_file}"'

    return response


def data_to_json(data):
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as file:
        json.dump(data, file, default=str)

    return create_response(file, 'json', 'application/json')


def data_to_csv(data):
    with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', suffix='.csv') as file:
        writer = csv.writer(file)

        writer.writerow(['id', 'participant', 'company', 'quiz', 'score', 'date passed', 'quiz_time', 'user_rating'])
        for item in data:
            score = Decimal(item['correct_answers'] / item['total_questions'] * 100).quantize(Decimal('1.00'))

            writer.writerow([
                 item['id'], item['participant']['username'], item['company']['name'], item['quiz']['title'], score,
                 item['updated_at'], item['quiz_time'], item['user_rating']
            ])

    return create_response(file, 'csv', 'text/csv')
