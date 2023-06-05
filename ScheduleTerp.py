import random
import requests
import re
import numpy as np

headers = {
  'Accept': 'application/json'
}

r = requests.get('https://api.planetterp.com/v1/professor', params={
  'name': 'Larry Herman'
}, headers = headers)

#print(r.json())


import requests
headers = {
  'Accept': 'application/json'
}

r = requests.get('https://api.planetterp.com/v1/grades', headers = headers, params={
      'course': 'ENGL101',
      'professor': 'William Pittman',
      'semester': '202108'
})

#print(r.json())

r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
  'course_id': 'CMSC330'
})
#print(r.json()[0])


class Section:
  def __init__(self, section_dict : dict) -> None:
    self.class_name = section_dict['course']
    self.section_num = section_dict['number']
    self.raw_meetings = []
    self.start_times = []

    my_lectures = []
    meetings = section_dict['meetings']
    for meeting in meetings:
      if (meeting['classtype'] != 'Discussion'):
        my_lectures.append(meeting)
      days = re.findall('^M|Tu|W|Th|F$', meeting['days'])
      for day in days:
        self.start_times.append(meeting['start_time'])
        raw_start_time = self.__get_raw_time(meeting['start_time'], day)
        raw_end_time = self.__get_raw_time(meeting['end_time'], day)
        self.raw_meetings.append((raw_start_time, raw_end_time))
        
    
    self.lectures = []
    for lecture in my_lectures:
      self.lectures.append(str(lecture['days']) + " " + str(lecture['start_time']) + "-" + str(lecture['end_time']))
    
    if (len(self.lectures) == 1):
      self.lectures = self.lectures[0]
      
    # TODO Set GPA from PlanetTerp
    self.gpa = (random.random() + 0.0001) * 4
    
  def conflicts_with_section(self, other : 'Section') -> bool:
    # True conflicts
    return any(not (other_interval[0] > interval[1] or other_interval[1] < interval[0]) for interval in self.raw_meetings for other_interval in other.raw_meetings)
    
  def conflicts_with_schedule(self, partial_schedule) -> bool:
    result = False
    # For each section in schedule, check if this conflicts. If any do, 
    # return true. Else return false.
    for section in partial_schedule:
      if (self.conflicts_with_section(section)):
        result = True
        break
    
    return result

  def __get_raw_time(self, time : str, day : str):
    day_converter = {'M': 0, 'Tu': 1, 'W': 2, 'Th' : 3, 'F': 4}
    hh, mm = map(int, time[:-2].split(':'))
    raw_time = hh + (mm / 60.0) + day_converter[day] * 24
    return raw_time
  
  def __str__(self) -> str:
    # TODO maybe add nicely formated day/time
    return self.class_name + " " + str(self.section_num) + " " + str(self.gpa) + " " + str(self.lectures)
  

mySection = Section(r.json()[0])
r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
  'course_id': 'ENES424'
})

secondSection = Section(r.json()[0])


def sig(x):
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
  
  start_time_score = sig(sum([sum([start_time_score_reference[start_time] for start_time 
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

def scheduling_algorithm():
  classes               = [[], [], []]
  all_schedules         = []
  conflicting_schedules = []

  # Test classes
  r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
    'course_id': 'CMSC330'
  })
  for section_dict in r.json():
    classes[0].append(Section(section_dict))
    
  r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
    'course_id': 'ENES424'
  })
  for section_dict in r.json():
    classes[1].append(Section(section_dict))
  

  r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
    'course_id': 'CMSC351'
  })
  
  for section_dict in r.json():
    classes[2].append(Section(section_dict))
  
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
          # TODO 4. Set more advanced weight here
          section_s.weight = section_s.gpa
          all_weights_0 = False
          
      # if all other weights are 0, add to conflicting_schedules
      if (all_weights_0):
        conflicting_schedules.append(running_schedule)
        break
      
      # add randomly selected section s in i to running_schedule
      my_weights = [section.weight for section in class_i]
      running_schedule.add(random.choices(class_i, [section.weight for section in class_i], k=1)[0])
    if (len(running_schedule) == len(classes)):
      # Only add the newly generated schedule if we didn't break early.
      all_schedules.append(running_schedule)
    
  score_and_sort_schedules(all_schedules)
  string_schedules = [[str(section) for section in schedule] for schedule in all_schedules]
  print(string_schedules)

def main():
  # call to algorithm
  scheduling_algorithm()
  

if __name__ == '__main__':
  main()

"""
TODO
Done - Make conflict work w/ additional days + times
1. Set GPA
2. Get our input from UMD IO + PlanetTerp
3. Add score + sort
4. Add more advanced weight selection
5. Front-end
"""