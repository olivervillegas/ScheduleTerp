#!/usr/bin/env python3
"""Auto-generate UMD schedules. The algorithm is O(n), but it is sampled-based
and thus not exact. Code is written for the ScheduleTerp website.
"""

import json
import re
import numpy as np
import random
from API import API
from Section import sig
from PlanetTerp import PlanetTerp

from Section import Section
from UMDio import UMDio
__author__ = "Oliver Villegas, Jaxon Lee"
__copyright__ = "Copyright 2023"
__credits__ = ["Jet Lee"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Oliver Villegas, Jaxon Lee"
__email__ = "j.oliver.vv@gmail.com, jaxondlee@gmail.com"
__status__ = "Development"

CURR_SEMESTER = 202308

def score_schedule(schedule: list):
    """Scores a schedule based on its GPA, the times of each class, and their relative times.

    Args:
        schedule (list): Schedule to score. It's a list of sections.

    Returns:
        int: the schedule's score
    """
    score = 0
    start_time_score_reference = {"7:00am": 0, "7:30am": 0, "8:00am": 0, "8:30am": 0,
                                  "9:00am": 3, "9:30am": 4, "10:00am": 10, "10:30am": 10,
                                  "11:00am": 10, "11:30am": 10, "12:00pm": 10, "12:30pm": 10,
                                  "1:00pm": 10, "1:30pm": 10, "2:00pm": 10, "2:30pm": 10,
                                  "3:00pm": 10,  "3:30pm": 10, "4:00pm": 9, "4:30pm": 8,
                                  "5:00pm": 7, "5:30pm": 6, "6:00pm": 5, "6:30pm": 4,
                                  "7:00pm": 3, "7:30pm": 2, "8:00pm": 1, "8:30pm": 0,
                                  "9:00pm": 0, "9:30pm": 0, "10:00pm": 0, "10:30pm": 0}

    average_gpa_score = sig(
        sum([section.gpa for section in schedule]) / len(schedule))

    start_time_score = sig(sum([sum([start_time_score_reference[start_time] for start_time
                                     in section.start_times]) for section in schedule]))
    # add {time gap b/w classes} score
    # Add geographical distances b/w classes
    # Add online vs in person
    # Add prefence f/ 4 day week or consolidated

    # User Profiles--
    # Commuter: consolidated, back to back... or doesn't care
    # Part time job worker: doesn't care about consolidation,
    #   but wants certain parts of the day open
    # "Class experience": in person, not consolidated
    # Night owl: no classes before 11
    # Freshman / Sophomore / Junior / Senior:
    # Only goes to lecture for exams: classes that don't require attendance

    relative_time_score = 0

    weight_dict = {"average_gpa": 10, "start_time": 1}

    return average_gpa_score * weight_dict['average_gpa'] + start_time_score * weight_dict['start_time']


def score_and_sort_schedules(all_schedules: list[list[Section]]):
    """Sorts all schedules from best to worst based on how good they are (subjective). For now, only take into account GPA.

    Args:
        all_schedules ([] : Section): The schedules to sort.
    """
    # Sort based on average GPA
    all_schedules.sort(key=lambda schedule: score_schedule(schedule))


def scheduling_algorithm(classes: list[list[Section]]):
    all_schedules = []
    conflicting_schedules = []

    for i in range(1000):
        available_classes = list(range(0, len(classes)))
        running_schedule = set()
        for j in range(len(classes)):
            # randomly select class i, where i not in used_class
            rand_index = random.choice(available_classes)
            available_classes.remove(rand_index)
            class_i = classes[rand_index]

            all_weights_0 = True
            # assign weight to i's sections based on GPA, conflicts
            for section_s in class_i:
                potential_schedule = running_schedule.copy()
                potential_schedule.add(section_s)
                # Check if section conflicts with schedule, if the newly proposed
                # schedule already exists or if it is known to be conflicting
                if section_s.conflicts_with_schedule(running_schedule) or any([x == potential_schedule for x in all_schedules]) or any([x == potential_schedule for x in conflicting_schedules]):
                    section_s.weight = 0
                else:
                    section_s.weight = section_s.get_weight()
                    all_weights_0 = False

            # if all other weights are 0, add to conflicting_schedules
            if (all_weights_0):
                conflicting_schedules.append(running_schedule)
                break

            # add randomly selected section s in i to running_schedule
            running_schedule.add(random.choices(
                class_i, [section.weight for section in class_i], k=1)[0])
        if (len(running_schedule) == len(classes)):
            # Only add the newly generated schedule if we didn't break early.
            all_schedules.append(running_schedule)

    score_and_sort_schedules(all_schedules)

    return all_schedules


def process_input(class_strings: list[str]):
    result = []
    classes = []
    grades = []
    average_gpas = []

    for one_class in class_strings:
        match one_class:
            # Follow their request, but warn them that they could fulfill both Gen-Eds at once
            case "Any":
                pass
            case 'FSAW' | 'FSAR' | 'FSMA' | 'FSOC' | 'DSHS' | 'DSHU' | "DSNS" | "DSNL" | 'DSSP' | 'DVCC' | 'DVUP' | 'SCIS':
                # TODO improve speed
                # TODO unify special + general case
                all_gen_ed_classes = UMDio.get_courses_that_fulfill_gen_ed(
                    one_class)

                gen_ed_sections = []
                for course in all_gen_ed_classes:
                    gen_ed_sections.extend(
                        UMDio.get_sections(course['course_id']))

                    avg_gpa, grade_dict = PlanetTerp.get_grades_from_course(
                        course)
                    grades.extend(grade_dict)

                average_gpas.append(avg_gpa)

                classes.append(gen_ed_sections)
            case _:
                classes.append(UMDio.get_sections(one_class))
                avg_gpa, grade_dict = PlanetTerp.get_grades(one_class)
                average_gpas.append(avg_gpa)
                grades.append(grade_dict)

    for i in range(len(classes)):
        section_arr = []
        grade_dict = grades[i]

        for section_dict in classes[i]:
            # TODO maybe add check if full
            section_arr.append(
                Section(section_dict, grade_dict, average_gpas[i]))

        result.append(section_arr)

    return result
        
# Note: This function takes a really long time. We can refactor it to use
# Async or multithreads.
def download_data_dump():
    data = ['CMSC132', 'MATH140']
    custom_data_dump = []
    # Load data
    with open("../custom_data_dump.json", "r") as f:
        data = json.load(f)
    # Process data
    for course_name in data:
        print(course_name)
        classes = process_input([course_name])
        custom_data_dump += classes
        print(classes)
    # Save data
    with open('custom_data_dump_2.txt', 'w') as convert_file:
        for course in custom_data_dump:
            for section in course:
                convert_file.write(section.toJson() + '\n')
                
def format_data_dump():
    data = {}
    # Load data
    with open("../custom_data_dump.txt", "r") as f:
        # Process data
        for line in f:
            (key, val) = line.rstrip().split(',', 1)
            key = re.search(".*\": \"(.*)\"", key).group(1)
            val = "{" + val
            val = json.loads(val)
            if key in data:
                data[key] += [val]
            else:
                data[key] = [val]
    # Save data
    with open('../custom_data_dump.json', 'w') as convert_file:
        data_dump = ""
        not_first_line = False
        data_dump += "{"
        for course_name in data:
            if not_first_line:
                    data_dump += ',\n'
            data_dump += "\"" + course_name + "\":  ["
            not_first_section = False
            for section in data[course_name]:
                if not_first_section:
                    data_dump += ','
                data_dump += json.dumps(section)
                not_first_section = True
            data_dump += "]"
            not_first_line = True
        data_dump += "}"
        convert_file.write(data_dump)

def fix_data_dump(has_univ_100_gpas=False, has_neg_1_gpas=False):
    data = {}
    courses_to_profs = {}
    # Load data
    with open("../custom_data_dump.json", "r") as f:
        data = json.load(f)
    with open("../courses_to_professors.json", "r") as f:
        courses_to_profs = json.load(f)
    # Process data
    UNIV100_GPA = 3.726264219878767
    FALLBACK_GPA = -1
    saved_grades_dict = {}  # Used to cache grade data for a course&professor combination
    for course_name in data:
        for section in data[course_name]:
            if has_univ_100_gpas:
                if section['gpa'] == UNIV100_GPA:
                    section_id = course_name + '-' + section['section_num']
                    section_result = API.request(f'https://api.umd.io/v1/courses/sections/{section_id}', params={'semester':CURR_SEMESTER})[0]
                    profs = []
                    if 'instructors' in section_result:
                        profs = section_result['instructors']
                    profs = profs or courses_to_profs[course_name]  # If this course has no profs, get the avg GPA of all profs for this course
                    gpas = []
                    for prof in profs:
                        if prof not in saved_grades_dict:
                            saved_grades_dict[prof] = (API.request('https://api.planetterp.com/v1/grades', params={
                    'professor': prof
                }))
                        gpas += [Section.get_gpa_given_prof(profs=profs, grades_dict=saved_grades_dict[prof], fallback_gpa=FALLBACK_GPA)]
                    gpas = [gpa for gpa in gpas if gpa != -1]  # Filter out -1 from average grade calculations
                    print(section_id, profs, gpas)
                    if len(gpas) != 0:
                        section['gpa'] = sum(gpas) / len(gpas)
                    else:
                        section['gpa'] = FALLBACK_GPA
            if has_neg_1_gpas:
                pass  # TODO: Implement
                    
    # Save data
    with open('../custom_data_dump_3.json', 'w') as convert_file:
        data_dump = ""
        not_first_line = False
        data_dump += "{"
        for course_name in data:
            if not_first_line:
                    data_dump += ',\n'
            data_dump += "\"" + course_name + "\":  ["
            not_first_section = False
            for section in data[course_name]:
                if not_first_section:
                    data_dump += ','
                data_dump += json.dumps(section)
                not_first_section = True
            data_dump += "]"
            not_first_line = True
        data_dump += "}"
        convert_file.write(data_dump)
    with open('../custom_data_dump_3_profs_to_gpa.json', 'w') as convert_file:
        convert_file.write(json.dumps(saved_grades_dict))

# # JET -- CALL THIS FUNCTION FROM THE FRONT END
# def get_schedules(input_classes: list(str)):
#     classes = process_input(input_classes)
#     all_schedules = scheduling_algorithm(classes)
#     string_schedules = [[str(section) for section in schedule]
#                         for schedule in all_schedules]

#     # TODO return some sort of formatted data that works well with the
#     # calendar library
#     return string_schedules


def main():
    print("Querying input from PlanetTerp and UMD.io...")
    # TODO query data in the background

    fix_data_dump(has_univ_100_gpas=True)
    return

    # data = []
    # for course_name in data:
    #     print(course_name)
    #     classes = process_input([course_name])
    # print(classes)

    # string_schedules = [[str(section) for section in schedule] for schedule in classes]
    # print(string_schedules)

    # NOTE: some HNUH classes are not in PlanetTerp
    print("Input processed!")

    all_schedules = scheduling_algorithm(classes)
    string_schedules = [[str(section) for section in schedule]
                        for schedule in all_schedules]

    # if (len(all_schedules) == 0):
    #   # TODO add some sort of error handling
    #   print("Error! UMD IO is down (Out of our control)! No schedules could be generated.")


if __name__ == '__main__':
    main()

"""
TODO
# Alpha Version
DONE- 1. Make conflict work w/ additional days + times
DONE-  Set GPA
  DONE- 1.5. Make GPA work for multiple professors in one class
DONE- Get our input from UMD IO + PlanetTerp
DONE- Add more advanced weight selection 
6. Front-end

# Beta version
-1. Send algorithm to Professor Childs / Professor Mount to see if we can write an academic paper on it
0. Draw out front-end using wireframing software
1. Add user account data (classes taken so far, fine with 8am's)
  1.5. Add corresponding course restrictions (freshman connection, junior status etc.)
2. Add boolean to exclude full classes 
  2.5 Discuss - recommend classes to waitlist? 
3. Discuss - Only consider grade data of last 5 years (or 10 semesters)?
4. Add Machine Learning f/ determining how good a schedule is based on classes that are in it
  4.5. Maybe consider 4 day week. Maybe ask questions about what people want as inputs for ML model
5. Get all classes into program (HNUH, etc.) May need to talk to PlanetTerp or UMD.io
6. Increase API call efficiency
7. Store restrictions in Section object in score+sort, remove restricted schedules from list
8. Choose random GenEd, or Any, or DSNS/DSHU, etc.
  8.5. Add "CMSC4" for 400 level courses



# Release versions
1. ScheduleTerp (MVP) 
2. ScheduleTerp+ (Users pay $$$, All small considerations, bus route to incentivize sustainable transportation, auto-register for classes)
    2.5 UMD Sustainability fund
3. Franchise out to other universities
"""
