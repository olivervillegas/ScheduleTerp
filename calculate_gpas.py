#!/usr/bin/env python3
"""Generate a dictionary of all the professors for the upcoming semester
so we can ship the data live. This will save computation time at runtime.
"""

from typing import Any, List
import numpy as np
import re
import requests
import random
import json
import collections


__author__ = "Jet Lee"
__copyright__ = "Copyright 2023"
__credits__ = ["Oliver Villegas, Jaxon Lee"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Jet Lee"
__email__ = "jetrlee@gmail.com"
__status__ = "Development"


headers = {
    'Accept': 'application/json'
}
'''
Internal API response sample:
course_name: string => 
{
    "course_gpa": float,
    "sections": [
        ("section_num": int,
        "section_meeting_times": [
            (start: (int), end: (int))
        1,
        "section_gpa": float)
}
'''

'''
TODO:
- list of all courses offered in 202308
- avg GPA for each course
- list of all section numbers for that course
- meeting times for each section
- gpa for each section
'''


class API:
    headers = {
        'Accept': 'application/json'
    }

    def request(link, params):
        return requests.get(link, headers=API.headers, params=params).json()


class Section:
    def __init__(self, class_name: str, section_num: int, instructors: list[str], course_gpa: float) -> None:
        self.class_name = class_name
        self.section_num = section_num
        self.instructors = instructors
        self.course_gpa = course_gpa
        self.meetings = []
        self.start_times = []


class Course:
    def __init__(self, instructors: list[str]) -> None:
        self.instructors = instructors
        self.gpa = 0

    def setGpa(self, gpa: float):
        self.gpa = gpa


CURR_SEMESTER = 202308


def get_sections(page: int):
    return requests.get(
        "https://api.umd.io/v1/courses/sections", params={'per_page': 100, 'page': page, 'semester': 202308}).json()


def get_courses_dict(page: int):
    return requests.get(
        "https://api.umd.io/v1/courses",
        params={'semester': CURR_SEMESTER, 'per_page': 100, 'page': page}).json()


def get_gpa_dict(name: str):
    return requests.get(
        "https://planetterp.com/api/v1/course", params={'name': name}).json()


def get_course_grades(name: str, professor: str):
    return requests.get(
        "https://planetterp.com/api/v1/grades", params={'course': name, "professor": professor}).json()


def get_grades_from_course(course_dict):
    try:
        avg_gpa = API.request('https://planetterp.com/api/v1/course', params={
            'name': course_dict['course_id']
        })['average_gpa']
        grades_dict = API.request('https://api.planetterp.com/v1/grades', params={
            'course': course_dict['course_id']
        })
    except KeyError:
        try:
            # Go through "formerly" known as
            former_name = course_dict['relationships']['formerly'][:-1]
            avg_gpa = API.request('https://planetterp.com/api/v1/course', params={
                'name': former_name
            })['average_gpa']
            grades_dict = API.request('https://api.planetterp.com/v1/grades', params={
                'course': former_name
            })
        except:
            shortened_name = course_dict['course_id'][:-1]
            similar_courses: dict = API.request('https://planetterp.com/api/v1/search', params={
                'query': shortened_name
            })
            while (len(similar_courses) == 0):
                shortened_name = shortened_name[:-1]
                similar_courses: dict = API.request('https://planetterp.com/api/v1/search', params={
                    'query': shortened_name
                })

            similar_course_name = random.choice(similar_courses)['name']
            avg_gpa = API.request('https://planetterp.com/api/v1/course', params={
                'name': similar_course_name
            })['average_gpa']
            grades_dict = API.request('https://api.planetterp.com/v1/grades', params={
                'course': similar_course_name
            })

    return avg_gpa, grades_dict


def main():
    sections_dict = {}
    all_lines: list(str) = []
    data = True
    page = 1
    with open("grades_dump.json", "r") as f:
        data = json.load(f)

    print(data['ARTH698'])

    with open('grades_dump_errors_custom.txt') as fp:
        line = fp.readline()
        while line:
            line: str = fp.readline()

    # while page < 2 and data:
    # data = get_sections(page=page)
    # for section in data:
    #     course_name = section['course']
    #     if course_name in sections_dict:
    #         sections_dict[course_name] += [section]
    #     else:
    #         sections_dict[course_name] = [section]
    # page += 1
    # print(page)
    # grades_dict[course_name] += list(set(grades) -
    #  set(grades_dict[course_name]))

    # with open('sections_dump.txt', 'w') as convert_file:
    #     convert_file.write(json.dumps(sections_dict))


if __name__ == '__main__':
    main()
