#!/usr/bin/env python3
"""Class for holding information about a particular section of a particular 
class. Stores class name, section number, and lecture times among other things.
"""

__author__     = "Oliver Villegas, Jaxon Lee"
__copyright__  = "Copyright 2023"
__credits__    = ["Jet Lee"]
__license__    = "MIT"
__version__    = "0.1.0"
__maintainer__ = "Oliver Villegas, Jaxon Lee"
__email__      = "j.oliver.vv@gmail.com, jaxondlee@gmail.com"
__status__     = "Development"

import re
import numpy as np
from typing import List

# TODO remove empty lectures from json, i.e. " -"
# [{"section_num": "0101", "gpa": 3.28, "lectures": ["W 4:00pm-5:45pm", " -"], "discussions": []}]
class Section:
  """Stores data for a section of a class.
  """
  def __init__(self, section_dict : dict, class_name : str) -> None:
    """Initializes the section

    Args:
        section_dict (dict): section data from ScheduleTerp API 
    """
    self.class_name   = class_name
    self.section_num  = section_dict['section_num']
    self.raw_meetings = []
    self.start_times  = []

    self.lectures = section_dict['lectures']
    
    # "lectures": "MWF 10:00am-10:50am"
    # "lectures": ["TuTh 2:00pm-3:15pm", "Th 6:00pm-6:50pm"]
    meetings : List[str] = []
    if (isinstance(section_dict['lectures'], str)):
      meetings.append(section_dict['lectures'])
    else:
      meetings.extend(section_dict['lectures'])
    
    
    meetings.extend(section_dict['discussions'])
    
    for meeting in meetings:
      # Extract all days for a particular meeting
      days = re.findall('^M|Tu|W|Th|F$', meeting)
      for day in days:
        # "meeting": "MWF 10:00am-10:50am"
        # start = "10:00am"
        # end = "10:50am"
        # Extract start and end times
        start, end = meeting.split(" ")[1].split("-")
        
        self.start_times.append(start)
        raw_start_time = self.__get_raw_time(start, day)
        raw_end_time = self.__get_raw_time(end, day)
        self.raw_meetings.extend([raw_start_time, raw_end_time])
    
    self.raw_meetings.sort()
  
    self.gpa = section_dict["gpa"]
    if (self.gpa == -1):
      # Average GPA across all classes
      self.gpa = 3.1
      

  def conflicts_with_section(self, other : 'Section') -> bool:
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
      my_curr_meeting    = self.raw_meetings[my_index]
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
      
      score = gpa_score * weight_dict['average_gpa'] + start_time_score * weight_dict['start_time'] 
      
      return score


  def __get_gpa_given_prof(self, profs : List[str], grades_dict, fallback_gpa):
    """Return the Professor's average GPA for this particular section.

    Args:
        prof (str): The professor to check
        grades_dict (dict): grades data for the section

    Returns:
        float: The average GPA of the Professor.
    """
    
    # TODO Maybe change W to 0.5
    past_sections = [section for section in grades_dict 
                     if section.get('professor') in profs]
    GPA_weights   = [4.0,4.0,3.7, 3.3,3.0,2.7, 2.3,2.0,1.7, 1.3,1.0,0.7, 0.0, 0.0]
    grades        = [0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0, 0.0, 0.0]
    for section in past_sections:
      grades[0]  += section['A+']
      grades[1]  += section['A']
      grades[2]  += section['A-']
      grades[3]  += section['B+']
      grades[4]  += section['B']
      grades[5]  += section['B-']
      grades[6]  += section['C+']
      grades[7]  += section['C']
      grades[8]  += section['C-']
      grades[9]  += section['D+']
      grades[10] += section['D']
      grades[11] += section['D-']
      grades[12] += section['F']
      grades[13] += section['W']
    
    total_grades = sum(grades)
    if (total_grades == 0):
      return fallback_gpa
    else:
      return sum([GPA_weights[i] * grades[i] for i in range(len(grades))]) / total_grades

  def __get_raw_time(self, time : str, day : str):
    """Convert AM/PM time to hours since 12:00am on Monday and return it."""
    day_converter = {'M': 0, 'Tu': 1, 'W': 2, 'Th' : 3, 'F': 4}
    hh, mm = map(int, time[:-2].split(':'))
    am_or_pm_multiplier = 0 if time[-2:] == "am" or hh == 12 else 1
    raw_time = hh + (mm / 60.0) + 12 * am_or_pm_multiplier + day_converter[day] * 24
    return raw_time
  
  def __str__(self) -> str:
    """Return neat string representation of this section."""
    return self.class_name + " " + str(self.section_num) + " " + str(self.gpa) + " " + str(self.lectures)
  
  def get_data(self):
    d = {}
    d['class_name'] = self.class_name
    d['section_num'] = self.section_num
    d['gpa'] = self.gpa
    d['lectures']  = self.lectures
    return d
  

# Code for dealing with schedules
def sig(x):
  """Apply sigmoid function to x and return it."""
  # Modified sigmoid function so that it doesn't level off so fast.
  return 1/(1 + np.exp(-1/10 * x))

def score_schedule(schedule : List[Section]):
  """Scores a schedule based on its GPA, the times of each class, and their relative times.

  Args:
      schedule (list): Schedule to score. It's a list of sections.

  Returns:
      float: the schedule's score
  """
  score = 0
  #any([section1.conflicts_with_section(section2) for section2 in schedule if section2 != section1] for section1 in schedule)
  # Check if schedule is possible before proceeding. If it's not possible, then 
  # simply return 0.
  is_possible_schedule = True
  for section1 in schedule:
    for section2 in schedule:
      if (section1 != section2):
        if (section1.conflicts_with_section(section2)):
          is_possible_schedule = False
          break
  if (is_possible_schedule):
    start_time_score_reference = {"7:00am": 0, "7:30am": 0, "8:00am": 0, "8:30am": 0,
                                "9:00am": 3, "9:30am": 4, "10:00am": 10, "10:30am": 10, 
                                "11:00am": 10, "11:30am": 10, "12:00pm": 10, "12:30pm": 10,
                                "1:00pm": 10, "1:30pm": 10, "2:00pm": 10, "2:30pm": 10,
                                "3:00pm": 10,  "3:30pm": 10, "4:00pm": 9, "4:30pm": 8,
                                "5:00pm": 7, "5:30pm": 6, "6:00pm": 5, "6:30pm": 4, 
                                "7:00pm": 3, "7:30pm": 2, "8:00pm": 1, "8:30pm": 0,
                                "9:00pm": 0, "9:30pm": 0, "10:00pm": 0, "10:30pm": 0}
    
    average_gpa_score = sig(sum([section.gpa for section in schedule]) / len(schedule))
    
    start_time_score  = sig(sum([sum([start_time_score_reference[start_time] for start_time 
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
    
    # TODO add this functionality
    relative_time_score = 0

    weight_dict = {"average_gpa": 10, "start_time": 1}
    score : float = average_gpa_score * weight_dict['average_gpa'] + start_time_score * weight_dict['start_time']
  return score


blacklisted_sections = []
def score_and_sort_schedules(all_schedules : List[List[Section]]):
  """Sorts all schedules from best to worst based on how good they are (subjective). For now, only take into account GPA.

  Args:
      all_schedules ([] : Section): The schedules to sort.
  """
  # Sort based on average GPA
  all_schedules.sort(key = lambda schedule: score_schedule(schedule))
  
  global blacklisted_sections
  blacklisted_sections.append(("CMSC131", "FC05"))
  blacklisted_sections.append(("CMSC132", "0203"))
  
  schedules_to_remove = []
  for schedule in all_schedules:
    for section in schedule:
      if ((section.class_name, section.section_num) in blacklisted_sections):
        schedules_to_remove.append(schedule)
        print("Found: " + str(section.class_name + section.section_num))
        string_schedule = [section.get_data() for section in schedule]
        print("Removed: " + str(string_schedule))
        break
  
  return [x for x in all_schedules if x not in schedules_to_remove]
  
