from openpyxl import load_workbook


def parse_excel(file):
    data = []
    workbook = load_workbook(file)
    for worksheet in workbook.worksheets:
        sheet_data = {}
        questions_data = []
        question = None

        for row_index, row in enumerate(worksheet.rows):
            if row_index < 3:
                sheet_data[row[0].internal_value] = row[1].internal_value
            elif row[0].internal_value == 'question':
                if question:
                    questions_data.append(question)
                question = {'question_text': row[1].internal_value, 'answers': []}
            else:
                question['answers'].append({'text': row[1].internal_value, 'is_right': row[2].internal_value == 'true'})

        questions_data.append(question)
        sheet_data['questions'] = questions_data
        data.append(sheet_data)

    return data
