import json
import amazon.ion.simpleion as ion

# Convert JSON data to a python dictionary.
data = {}
with open("./custom_data_dump_3.json", "r") as f:
    data = json.load(f)

# Create new data dump where the key is "Item" and values contain course_id
t = open("./custom_data_dump_4.txt", "w")
not_first_line = False
for course in data:
    if not_first_line:
        t.write('\n')
    for section in data[course]:
        section['gpa'] = float(section['gpa'])  # Cast GPA to a float so it can be read as an ION
    data[course] = {"course_id": course, "sections": data[course]}
    t.write('{"Item": ' + json.dumps(data[course]) + '}')
    not_first_line = True
t.close()

# Get list of lines from data dump.
with open("./custom_data_dump_4.txt", "r") as f:
    data = f.read().split('\n')

# Convert each line to its own ION object and write it to a new data dump.
with open("dynamo_custom_data_dump.ion", "w") as f:
    not_first_line = False
    for line in data:
        if not_first_line:
            f.write('\n')
        obj = ion.loads(line)
        f.write(ion.dumps(obj,binary=False))
        not_first_line = True

# Test final data dump.
with open("dynamo_custom_data_dump.ion", "r") as f:
    data = ion.load(f, single_value=False)
    print(data)