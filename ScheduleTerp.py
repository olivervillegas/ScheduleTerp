import random
import requests

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
      'course': 'CMSC351'
})

print(r.json())

class Section:
  def __init__(self, class_name, section_num, gpa, days, time_start, time_end) -> None:
    self.class_name = class_name
    self.section_num = section_num
    self.gpa = gpa
    self.weight = 0
    self.days = days
    self.time_start = time_start
    self.time_end = time_end
    
  def __init__(self, class_name, section_num, gpa, time) -> None:
    """
    Dummy initializer
    """
    self.class_name = class_name
    self.section_num = section_num
    self.gpa = gpa
    self.time = time
    self.weight = 0
    
  def conflicts_with_section(self, other : 'Section') -> bool:
    # Simplified conflicts
    return self.time == other.time or self.class_name == other.class_name
    
  def conflicts_with_schedule(self, partial_schedule) -> bool:
    result = False
    # For each section in schedule, check if this conflicts. If any do, 
    # return true. Else return false.
    for section in partial_schedule:
      if (self.conflicts_with_section(section)):
        result = True
        break
    
    return result
  
  def __str__(self) -> str:
    return self.class_name + " " + str(self.section_num) + " " + str(self.gpa) + " " + str(self.time)
  
        
  

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
  print(string_schedules)

def main():
  # call to algorithm
  scheduling_algorithm()

if __name__ == '__main__':
  main()

"""
TODO
1. Get our input from UMD IO + PlanetTerp
2. Make conflict work w/ additional days + times
3. Add score + sort
4. Add more advanced weight selection
5. Front-end
"""