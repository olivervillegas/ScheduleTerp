#!/usr/bin/env python3
"""Auto-generate UMD schedules. The algorithm is O(n), but it is sampled-based
and thus not exact. Code is written for the ScheduleTerp website.
"""

__author__     = "Oliver Villegas, Jaxon Lee"
__copyright__  = "Copyright 2023"
__credits__    = ["Jet Lee"]
__license__    = "MIT"
__version__    = "0.1.0"
__maintainer__ = "Oliver Villegas, Jaxon Lee"
__email__      = "j.oliver.vv@gmail.com, jaxondlee@gmail.com"
__status__     = "Development"

import random
import requests
import re
import numpy as np


class Section:
  """Stores data for a section of a class.
  """
  def __init__(self, section_dict : dict, grades_dict : dict, course_gpa : float) -> None:
    """Initializes the section

    Args:
        section_dict (dict): section data from UMD.io API 
        grades_dict (dict): grades data from PlanetTerp API
    """
    self.class_name   = section_dict['course']
    self.section_num  = section_dict['number']
    self.instructors  = section_dict['instructors']
    self.raw_meetings = []
    self.start_times  = []

    my_lectures = []
    meetings = section_dict['meetings']
    for meeting in meetings:
      if (meeting['classtype'] != 'Discussion'):
        my_lectures.append(meeting)
      # Extract all days for a particular meeting
      days = re.findall('^M|Tu|W|Th|F$', meeting['days'])
      for day in days:
        self.start_times.append(meeting['start_time'])
        raw_start_time = self.__get_raw_time(meeting['start_time'], day)
        raw_end_time = self.__get_raw_time(meeting['end_time'], day)
        self.raw_meetings.extend([raw_start_time, raw_end_time])
    
    self.raw_meetings.sort()
    
    self.lectures = []
    for lecture in my_lectures:
      self.lectures.append(str(lecture['days']) + " " + str(lecture['start_time']) 
                           + "-" + str(lecture['end_time']))
    
    if (len(self.lectures) == 1):
      self.lectures = self.lectures[0]
    
    # Divide by zero occurs if professor doesn't exist
    try:
      if len(section_dict['instructors']) == 1:
        self.gpa = self.__get_gpa_given_prof(section_dict['instructors'][0], grades_dict)
      else:
        for instructor in section_dict['instructors']:
          # if profesor has no grada data
            # return average GPA of course as a whole
          pass
          # else if professor has grade data
        self.gpa = 1
    except ZeroDivisionError:
      self.gpa = course_gpa

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
    #return any(not (other_interval[0] > interval[1] or other_interval[1] < interval[0]) for interval in self.raw_meetings for other_interval in other.raw_meetings)
    
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

  def __get_gpa_given_prof(self, prof : str, grades_dict):
    """Return the Professor's average GPA for this particular section.

    Args:
        prof (str): The professor to check
        grades_dict (dict): grades data for the section

    Returns:
        float: The average GPA of the Professor.
    """
    # TODO account for W's here as well
    past_sections = [d for d in grades_dict if d.get('professor') == prof]
    GPA_weights   = [4.0,4.0,3.7, 3.3,3.0,2.7, 2.3,2.0,1.7, 1.3,1.0,0.7, 0.0]
    grades        = [0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0, 0.0]
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
    
    return sum([GPA_weights[i] * grades[i] for i in range(len(grades))]) / sum(grades)

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
  
headers = {
  'Accept': 'application/json'
}

r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
  'course_id': 'CMSC330'
})

#print(r.json())

# mySection = Section(r.json()[0], pltp_r)
# print(mySection)

# print(mySection.raw_meetings)
# print(mySection.conflicts_with_section(mySection)) 

# r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
#   'course_id': 'ENES424'
# })

# secondSection = Section(r.json()[0], pltp_r)


def sig(x):
  """Apply sigmoid function to x and return it."""
  # Modified sigmoid function so that it doesn't level off so fast.
  return 1/(1 + np.exp(-1/10 * x))

def score_schedule(schedule : list):
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
  
  average_gpa_score = sig(sum([section.gpa for section in schedule]) / len(schedule))
  
  start_time_score  = sig(sum([sum([start_time_score_reference[start_time] for start_time 
                               in section.start_times]) for section in schedule]))
  
  relative_time_score = 0

  weight_dict = {"average_gpa": 10, "start_time": 1}
  
  return average_gpa_score * weight_dict['average_gpa'] + start_time_score * weight_dict['start_time']

def score_and_sort_schedules(all_schedules : list[list[Section]]):
  """Sorts all schedules from best to worst based on how good they are (subjective). For now, only take into account GPA.

  Args:
      all_schedules ([] : Section): The schedules to sort.
  """
  # Sort based on average GPA
  all_schedules.sort(key = lambda schedule: score_schedule(schedule))

def scheduling_algorithm(classes : list[list[Section]]):
  #classes               = [[], [], []]
  all_schedules         = []
  conflicting_schedules = []


  # Test classes
  # r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
  #   'course_id': 'CMSC330'
  # })
  # for section_dict in r.json():
  #   classes[0].append(Section(section_dict))
    
  # r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
  #   'course_id': 'ENES424'
  # })
  # for section_dict in r.json():
  #   classes[1].append(Section(section_dict))
  

  # r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
  #   'course_id': 'CMSC351'
  # })
  
  # for section_dict in r.json():
  #   classes[2].append(Section(section_dict))
  
  # End test classes
  
  for i in range(1000):
    available_classes = list(range(0, len(classes)))
    running_schedule  = set()
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
          section_s.weight = section_s.gpa
          all_weights_0 = False
          
      # if all other weights are 0, add to conflicting_schedules
      if (all_weights_0):
        conflicting_schedules.append(running_schedule)
        break
      
      # add randomly selected section s in i to running_schedule
      running_schedule.add(random.choices(class_i, [section.weight for section in class_i], k=1)[0])
    if (len(running_schedule) == len(classes)):
      # Only add the newly generated schedule if we didn't break early.
      all_schedules.append(running_schedule)
    
  score_and_sort_schedules(all_schedules)
  string_schedules = [[str(section) for section in schedule] for schedule in all_schedules]
  print(string_schedules)

def process_input(class_strings : list[str]):
  result = []
  classes = []
  grades  = []
  average_gpas = []

  for one_class in class_strings:
    classes.append(requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
      'course_id': one_class
      }).json())
    grades.append(requests.get('https://api.planetterp.com/v1/grades', headers = headers, params={
      'course': one_class
      }).json())
    average_gpas.append(requests.get('https://planetterp.com/api/v1/course', headers = headers, params={
      'name': one_class
      }).json()['average_gpa'])

  for i in range(len(classes)):
    section_arr = []
    grade_dict = grades[i]

    for section_dict in classes[i]:
      # TODO maybe add check if full
      section_arr.append(Section(section_dict, grade_dict, average_gpas[i]))

    result.append(section_arr)
    
  return result
  
  


def main():
  print("Querying input from PlanetTerp and UMD.io...")
  # TODO query data in the background
  my_input = ["ANTH451", "CMSC425", "CMSC426", "CMSC436", "ENGL393"]
  classes = process_input(my_input)
  
  # NOTE: some HNUH classes are not in PlanetTerp
  print("Input processed!")
  
  scheduling_algorithm(classes)

if __name__ == '__main__':
  main()

"""
TODO
# Alpha Version
DONE- 1. Make conflict work w/ additional days + times
DONE-  Set GPA
  1.5. Make GPA work for multiple professors in one class
DONE- Get our input from UMD IO + PlanetTerp
DONE- Add score + sort
  3.5. Add virtual meeting functionality
4. Choose random GenEd, or Any, or DSNS/DSHU, etc.
5. Add more advanced weight selection 
6. Front-end

# Beta version
1. Add user account data (classes taken so far, fine with 8am's)
  1.5. Add corresponding course restrictions (freshman connection, junior status etc.)
2. Add boolean to exclude full classes 
3. Only consider grade data of last 5 years (or 10 semesters)
4. Add Machine Learning f/ determining how good a schedule is based on classes that are in it
  4.5. Maybe consider 4 day week. Maybe ask questions about what people want as inputs for ML model


# Release versions
1. ScheduleTerp (MVP) 
2. ScheduleTerp+ (Users pay $$$, All small considerations, bus route to incentivize sustainable transportation)
    2.5 UMD Sustainability fund
3. Franchise out to other universities
"""