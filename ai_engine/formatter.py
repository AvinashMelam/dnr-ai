import json


def format_answer(records):

    if not records:

        return "No records found."

    if len(records)==1:

        row = records[0]

        answer=""

        for k,v in row.items():

            answer += f"{k} : {v}\n"

        return answer

    return json.dumps(records,indent=4)