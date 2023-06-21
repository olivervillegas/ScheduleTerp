#!/usr/bin/env python3

from API import API

class UMDio(API):
    def get_courses_that_fulfill_gen_ed(gen_ed_name):
        return API.request('https://api.umd.io/v1/courses', params={
            'gen_ed': gen_ed_name,
            'per_page': 100
        })

    def get_sections(course_name):
        return API.request('https://api.umd.io/v1/courses/sections', params={
            'course_id': course_name,
            'per_page': 100
        })
