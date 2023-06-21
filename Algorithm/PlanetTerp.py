#!/usr/bin/env python3

import random
from API import API

class PlanetTerp(API):
    def get_grades(course_name: str, course_dict=None):
        course_details = course_dict or API.request(f'https://api.umd.io/v1/courses/{course_name}', params={
        })[0]
        avg_gpa = None
        grades_dict = None

        former_name = course_details['relationships']['formerly']

        course_results = API.request('https://planetterp.com/api/v1/course', params={
            'name': course_name
        })

        if 'average_gpa' in course_results:
            avg_gpa = course_results['average_gpa']
        elif former_name:
            course_results = API.request('https://planetterp.com/api/v1/course', params={
                'name': former_name
            })
            if 'average_gpa' in course_results:
                avg_gpa = course_results['average_gpa']

        try:
            grades_dict = API.request('https://api.planetterp.com/v1/grades', params={
                'course': course_name
            })
        except KeyError:  # No grades for this course
            try:
                # Go through "formerly" known as
                grades_dict = API.request('https://api.planetterp.com/v1/grades', params={
                    'course': former_name
                })
            except:
                pass

        if not avg_gpa or not grades_dict:
            backup_avg_gpa, backup_grades_dict = PlanetTerp.__get_similar_courses__(
                course_name=course_name)
            avg_gpa = avg_gpa or backup_avg_gpa
            grades_dict = grades_dict or backup_grades_dict

        # https://planetterp.com/api/v1/grades?course=cmsc330
        # [{"course":"CMSC330","professor":"Chau-Wen Tseng","semester":"201201","section":"0101",
        #   "A+":1,"A":2,"A-":4,"B+":4,"B":3,"B-":2,"C+":2,"C":6,"C-":0,"D+":0,"D":1,"D-":0,"F":1,"W":1,"Other":0}, ...]
        return avg_gpa, grades_dict

    def get_grades_from_course(course_dict):
        return PlanetTerp.get_grades(course_dict['course_id'], course_dict)

    def __get_similar_courses__(course_name: str) -> str:
        shortened_name = course_name[:-1]
        print(shortened_name)
        similar_courses: dict = API.request('https://planetterp.com/api/v1/search', params={
            'query': shortened_name
        })
        # Continue shortening the name until a search result returns any courses.
        original_length = len(shortened_name)
        runs = 0
        custom = False
        while (len(similar_courses) == 0 and runs < original_length):
            shortened_name = shortened_name[:-1]
            similar_courses: dict = API.request('https://planetterp.com/api/v1/search', params={
                'query': shortened_name
            })
            print(shortened_name)
            similar_courses = list(filter(
                lambda x: (x['type'] == 'course'), similar_courses))
            runs += 1
        else:  # TODO: How should we handle the case where the department or class has never existed before?
            similar_course_name = 'UNIV100'

        similar_course_name = similar_course_name or random.choice(similar_courses)[
            'name']
        avg_gpa = API.request('https://planetterp.com/api/v1/course', params={
            'name': similar_course_name
        })['average_gpa']
        grades_dict = API.request('https://api.planetterp.com/v1/grades', params={
            'course': similar_course_name
        })
        if custom:
            avg_gpa = -1
        return avg_gpa, grades_dict
