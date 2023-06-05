import random
import requests
import re

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


r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
  'course_id': 'CMSC330'
})


class Section:
  def __init__(self, section_dict : dict, grades_dict : dict) -> None:
    self.class_name   = section_dict['course']
    self.section_num  = section_dict['number']
    self.instructors  = section_dict['instructors']
    self.raw_meetings = []
    
    meetings = section_dict['meetings']
    for meeting in meetings:
      days = re.findall('^M|Tu|W|Th|F$', meeting['days'])
      for day in days:
        start_time = self.__get_raw_time(meeting['start_time'], day)
        end_time = self.__get_raw_time(meeting['end_time'], day)
        self.raw_meetings.append((start_time, end_time))
    
    # TODO Set GPA from PlanetTerp
    if len(section_dict['instructors']) == 1:
      self.gpa = self.__get_gpa_given_prof(section_dict['instructors'][0], grades_dict)
    else:
      pass

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

  def __get_gpa_given_prof(self, prof : str, grades_dict):
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
    day_converter = {'M': 0, 'Tu': 1, 'W': 2, 'Th' : 3, 'F': 4}
    hh, mm = map(int, time[:-2].split(':'))
    raw_time = hh + (mm / 60.0) + day_converter[day] * 24
    return raw_time
  
  def __str__(self) -> str:
    # TODO maybe add nicely formated day/time
    return self.class_name + " " + str(self.section_num) + " " + str(self.gpa)
  

mySection = Section(r.json()[0], pltp_r)
print(mySection)

print(mySection.raw_meetings)
print(mySection.conflicts_with_section(mySection)) 

r = requests.get('https://api.umd.io/v1/courses/sections', headers=headers, params={
  'course_id': 'ENES424'
})

secondSection = Section(r.json()[0], pltp_r)

print(mySection.conflicts_with_section(secondSection))

def score_and_sort_schedules(all_schedules):
  pass

def scheduling_algorithm():
  classes               = [[], [], []]
  all_schedules         = []
  conflicting_schedules = []

  # Test classes
  classes[0].append(Section('CMSC330', section_num=100, gpa=3.5, time=10))
  classes[0].append(Section('CMSC330', section_num=200, gpa=3.0, time=11))
  
  classes[1].append(Section('CMSC351', section_num=100, gpa=3.9, time=10))
  classes[1].append(Section('CMSC351', section_num=200, gpa=3.1, time=11))

  classes[2].append(Section('ENES210', section_num=909, gpa=2.7, time=10))
  classes[2].append(Section('ENES210', section_num=908, gpa=2.4, time=5))
  
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
  #print(string_schedules)

def main():
  # call to algorithm
  #scheduling_algorithm()
  pass

if __name__ == '__main__':
  main()

"""
TODO
Done - 1. Make conflict work w/ additional days + times
1. Set GPA
  1.5. Make GPA work for multiple professors in one class
2. Get our input from UMD IO + PlanetTerp
3. Add score + sort
4. Add more advanced weight selection
5. Front-end
"""