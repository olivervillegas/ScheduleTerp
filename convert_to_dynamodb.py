import json
from dynamodb_json import json_util

## Deprecated: The DynamoDB Json imports are funky. We are switching to ION instead.

data = {}
with open("./custom_data_dump_3.json", "r") as f:
    data = json.load(f)

f = open("dynamo_custom_data_dump.json", "w")

not_first_line = False
f.write('{')
for course in data:
    if not_first_line:
        f.write(',\n')
    f.write('"Item": { "course_id": { "S" : "' + course + '"}, ')
    f.write('"sections": { "L": ' + json_util.dumps(data[course]) + '}')
    f.write('}')
    not_first_line = True
f.write('}')
f.close()
