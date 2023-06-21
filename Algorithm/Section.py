#!/usr/bin/env python3

import re
import json
import numpy as np

def sig(x):
    """Apply sigmoid function to x and return it."""
    # Modified sigmoid function so that it doesn't level off so fast.
    return 1/(1 + np.exp(-1/10 * x))

class Section:
    """Stores data for a section of a class.
    """

    def __init__(self, section_dict: dict, grades_dict: dict, course_gpa: float) -> None:
        """Initializes the section

        Args:
            section_dict (dict): section data from UMD.io API 
            grades_dict (dict): grades data from PlanetTerp API
        """
        self.class_name = section_dict['course']
        self.section_num = section_dict['number']
        self.instructors = section_dict['instructors']
        self.raw_meetings = []
        self.start_times = []

        my_lectures = []
        my_discussions = []
        meetings = section_dict['meetings']
        for meeting in meetings:
            if (meeting['classtype'] != 'Discussion'):
                my_lectures.append(meeting)
            else:
                my_discussions.append(meeting)
            # Extract all days for a particular meeting
            days = re.findall('^M|Tu|W|Th|F$', meeting['days'])
            for day in days:
                self.start_times.append(meeting['start_time'])
                raw_start_time = self.__get_raw_time(
                    meeting['start_time'], day)
                raw_end_time = self.__get_raw_time(meeting['end_time'], day)
                self.raw_meetings.extend([raw_start_time, raw_end_time])

        self.raw_meetings.sort()

        self.lectures = []
        for lecture in my_lectures:
            self.lectures.append(str(lecture['days']) + " " + str(lecture['start_time'])
                                 + "-" + str(lecture['end_time']))
        self.discussions = []
        for discussion in my_discussions:
            self.discussions.append(str(discussion['days']) + " " + str(discussion['start_time'])
                                 + "-" + str(discussion['end_time']))

        if (len(self.lectures) == 1):
            self.lectures = self.lectures[0]

        if (grades_dict == None or len(section_dict['instructors']) == 0):
            self.gpa = course_gpa
        else:
            self.gpa = Section.get_gpa_given_prof(
                section_dict['instructors'], grades_dict, fallback_gpa=course_gpa)

    def json_serialize(self):
        return {'course': self.class_name, 'section_num': self.section_num, 'gpa': self.gpa, 'lectures': self.lectures, 'discussions': self.discussions}

    def toJson(self):
        return json.dumps(self, default=lambda o: o.json_serialize())

    def conflicts_with_section(self, other: 'Section') -> bool:
        """Return true if this section conflicts with the other section.

        Go through both section times in order until either a double start time 
        (even index + even index) or double end time (odd index + odd index) occurs.
        We can detect both by checking if the sum is even. This algorithm is O(n).

        Returns:
            bool: Return true if the two sections conflict (can't schedule them
            together).
        """
        result = False
        my_index = 0
        other_index = 0
        last_index_checked = -1
        while (my_index < len(self.raw_meetings)
               and other_index < len(other.raw_meetings)):
            my_curr_meeting = self.raw_meetings[my_index]
            other_curr_meeting = other.raw_meetings[other_index]
            if (my_curr_meeting < other_curr_meeting):
                if ((last_index_checked + my_index) % 2 == 0):
                    result = True
                    break
                last_index_checked = my_index
                my_index += 1
            else:
                if ((last_index_checked + other_index) % 2 == 0):
                    result = True
                    break
                last_index_checked = other_index
                other_index += 1

        return result

    def conflicts_with_schedule(self, partial_schedule) -> bool:
        """Return true if this section conflicts with anything in the schedule."""
        result = False
        # For each section in schedule, check if this conflicts. If any do,
        # return true. Else return false.
        for section in partial_schedule:
            if (self.conflicts_with_section(section)):
                result = True
                break

        return result

    def get_weight(self) -> float:
        score = 0
        start_time_score_reference = {"7:00am": 0, "7:30am": 0, "8:00am": 0, "8:30am": 0,
                                      "9:00am": 3, "9:30am": 4, "10:00am": 10, "10:30am": 10,
                                      "11:00am": 10, "11:30am": 10, "12:00pm": 10, "12:30pm": 10,
                                      "1:00pm": 10, "1:30pm": 10, "2:00pm": 10, "2:30pm": 10,
                                      "3:00pm": 10,  "3:30pm": 10, "4:00pm": 9, "4:30pm": 8,
                                      "5:00pm": 7, "5:30pm": 6, "6:00pm": 5, "6:30pm": 4,
                                      "7:00pm": 3, "7:30pm": 2, "8:00pm": 1, "8:30pm": 0,
                                      "9:00pm": 0, "9:30pm": 0, "10:00pm": 0, "10:30pm": 0}

        gpa_score = sig(self.gpa)

        start_time_score = sum([start_time_score_reference[start_time] for
                                start_time in self.start_times])

        relative_time_score = 0

        weight_dict = {"average_gpa": 10, "start_time": 1}

        score = gpa_score * weight_dict['average_gpa'] + \
            start_time_score * weight_dict['start_time']

        return score

    def get_gpa_given_prof(profs: list[str], grades_dict, fallback_gpa):
        """Return the Professor's average GPA for this particular section.

        Args:
            prof (str): The professor to check
            grades_dict (dict): grades data for the section

        Returns:
            float: The average GPA of the Professor.
        """

        # TODO Maybe change W to 0.5
        past_sections = [section for section in grades_dict
                         if 'professor' in section and section['professor'] in profs]
        GPA_weights = [4.0, 4.0, 3.7, 3.3, 3.0, 2.7,
                       2.3, 2.0, 1.7, 1.3, 1.0, 0.7, 0.0, 0.0]
        grades = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for section in past_sections:
            grades[0] += section['A+']
            grades[1] += section['A']
            grades[2] += section['A-']
            grades[3] += section['B+']
            grades[4] += section['B']
            grades[5] += section['B-']
            grades[6] += section['C+']
            grades[7] += section['C']
            grades[8] += section['C-']
            grades[9] += section['D+']
            grades[10] += section['D']
            grades[11] += section['D-']
            grades[12] += section['F']
            grades[13] += section['W']

        total_grades = sum(grades)
        if (total_grades == 0):
            return fallback_gpa
        else:
            return sum([GPA_weights[i] * grades[i] for i in range(len(grades))]) / total_grades

    def __get_raw_time(self, time: str, day: str):
        """Convert AM/PM time to hours since 12:00am on Monday and return it."""
        day_converter = {'M': 0, 'Tu': 1, 'W': 2, 'Th': 3, 'F': 4}
        hh, mm = map(int, time[:-2].split(':'))
        am_or_pm_multiplier = 0 if time[-2:] == "am" or hh == 12 else 1
        raw_time = hh + (mm / 60.0) + 12 * \
            am_or_pm_multiplier + day_converter[day] * 24
        return raw_time

    def __str__(self) -> str:
        """Return neat string representation of this section."""
        return self.class_name + " " + str(self.section_num) + " " + str(self.gpa) + " " + str(self.lectures)
