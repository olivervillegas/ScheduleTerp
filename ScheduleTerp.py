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

import json
import random
import requests
import re
import json
import numpy as np

class API:
  headers = {
    'Accept': 'application/json'
  }
  
  def request(link, params):
    return requests.get(link, headers = API.headers, params = params).json()

class PlanetTerp(API):
  def get_grades(course_name):
    avg_gpa = API.request('https://planetterp.com/api/v1/course', params = {
      'name': course_name
      })['average_gpa']
    grades_dict = API.request('https://api.planetterp.com/v1/grades', params = {
      'course': course_name
    })
    # https://planetterp.com/api/v1/grades?course=cmsc330
    # [{"course":"CMSC330","professor":"Chau-Wen Tseng","semester":"201201","section":"0101",
    #   "A+":1,"A":2,"A-":4,"B+":4,"B":3,"B-":2,"C+":2,"C":6,"C-":0,"D+":0,"D":1,"D-":0,"F":1,"W":1,"Other":0}, ...]
    return avg_gpa, grades_dict
    
  def get_grades_from_course(course_dict):
    try:
      avg_gpa = API.request('https://planetterp.com/api/v1/course', params ={ 
        'name': course_dict['course_id']
        })['average_gpa']
      grades_dict = API.request('https://api.planetterp.com/v1/grades', params = {
        'course': course_dict['course_id']
          })
    except KeyError:
      try: 
        # Go through "formerly" known as
        former_name = course_dict['relationships']['formerly'][:-1]
        avg_gpa = API.request('https://planetterp.com/api/v1/course', params = {
          'name': former_name
          })['average_gpa']
        grades_dict = API.request('https://api.planetterp.com/v1/grades', params = {
          'course': former_name
          })
      except:
        # Try to find a similar course if all else fails. 
        shortened_name = course_dict['course_id'][:-1]
        similar_courses : dict = API.request('https://planetterp.com/api/v1/search', params = {
          'query': shortened_name
        })
        while (len(similar_courses) == 0):
          shortened_name = shortened_name[:-1]
          similar_courses : dict = API.request('https://planetterp.com/api/v1/search', params = {
            'query': shortened_name
          })
        
        similar_course_name = random.choice(similar_courses)['name']
        avg_gpa = API.request('https://planetterp.com/api/v1/course', params = {
          'name': similar_course_name
          })['average_gpa']
        grades_dict = API.request('https://api.planetterp.com/v1/grades', params = {
          'course': similar_course_name
          })
      
    return avg_gpa, grades_dict
        
    
# to get grade data
class UMDio(API):
  def get_courses_that_fulfill_gen_ed(gen_ed_name):
    return API.request('https://api.umd.io/v1/courses', params = {
          'gen_ed': gen_ed_name,
          'per_page': 100
          })
  
  def get_sections(course_name):
    return API.request('https://api.umd.io/v1/courses/sections', params = {
      'course_id': course_name,
      'per_page': 100
      })

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
    meetings : list[str] = []
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
      
  
  
  # def __init__(self, section_dict : dict, grades_dict : dict, course_gpa : float) -> None:
  #   """Initializes the section

  #   Args:
  #       section_dict (dict): section data from UMD.io API 
  #       grades_dict (dict): grades data from PlanetTerp API
  #   """
  #   self.class_name   = section_dict['course']
  #   self.section_num  = section_dict['number']
  #   self.instructors  = section_dict['instructors']
  #   self.raw_meetings = []
  #   self.start_times  = []

  #   my_lectures = []
  #   meetings = section_dict['meetings']
  #   for meeting in meetings:
  #     if (meeting['classtype'] != 'Discussion'):
  #       my_lectures.append(meeting)
  #     # Extract all days for a particular meeting
  #     days = re.findall('^M|Tu|W|Th|F$', meeting['days'])
  #     for day in days:
  #       self.start_times.append(meeting['start_time'])
  #       raw_start_time = self.__get_raw_time(meeting['start_time'], day)
  #       raw_end_time = self.__get_raw_time(meeting['end_time'], day)
  #       self.raw_meetings.extend([raw_start_time, raw_end_time])
    
  #   self.raw_meetings.sort()
    
  #   self.lectures = []
  #   for lecture in my_lectures:
  #     self.lectures.append(str(lecture['days']) + " " + str(lecture['start_time']) 
  #                          + "-" + str(lecture['end_time']))
    
  #   if (len(self.lectures) == 1):
  #     self.lectures = self.lectures[0]
    
  #   if (grades_dict == None or len(section_dict['instructors']) == 0):
  #     self.gpa = course_gpa
  #   else:
  #     self.gpa = self.__get_gpa_given_prof(section_dict['instructors'], grades_dict, fallback_gpa=course_gpa)
    

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


  def __get_gpa_given_prof(self, profs : list[str], grades_dict, fallback_gpa):
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

def sig(x):
  """Apply sigmoid function to x and return it."""
  # Modified sigmoid function so that it doesn't level off so fast.
  return 1/(1 + np.exp(-1/10 * x))

def score_schedule(schedule : list[Section]):
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
    
    
    relative_time_score = 0

    weight_dict = {"average_gpa": 10, "start_time": 1}
    score : float = average_gpa_score * weight_dict['average_gpa'] + start_time_score * weight_dict['start_time']
  return score

def score_and_sort_schedules(all_schedules : list[list[Section]]):
  """Sorts all schedules from best to worst based on how good they are (subjective). For now, only take into account GPA.

  Args:
      all_schedules ([] : Section): The schedules to sort.
  """
  # Sort based on average GPA
  all_schedules.sort(key = lambda schedule: score_schedule(schedule))

# Different Methods
def genetic_method(classes: list[list[Section]]):
  POPULATION_SIZE = 100
  GENERATIONS = 100
  MUTATION_RATE = 0.1
  
  # Generate an initial population of schedules
  population = generate_initial_population(classes, POPULATION_SIZE)
  
  for generation in range(GENERATIONS):
      # Evaluate the fitness of each schedule in the population
      fitness_scores = evaluate_fitness(population)
      
      # Perform selection to choose parents for crossover
      parents = selection(population, fitness_scores)
      
      # Create the next generation through crossover
      offspring = crossover(parents)
      
      # Apply mutation to the offspring
      mutated_offspring = mutation(offspring, MUTATION_RATE)
      
      # Replace the old population with the new generation
      population = mutated_offspring
  
  # Sort the final population by fitness
  population.sort(key=lambda x: evaluate_fitness([x])[0], reverse=True)
  
  # Return the schedules from the final population
  return population

def generate_initial_population(classes, population_size):
  # TODO add functionality for population size
  population = sampling_based_method(classes)
  
  population = [list(schedule) for schedule in population]
  
  return population

def evaluate_fitness(population : list[list[Section]]):
  fitness_scores = []
  
  for schedule in population:
    # Calculate the fitness score for a schedule
    fitness_score = calculate_fitness(schedule)
    fitness_scores.append(fitness_score)
  
  return fitness_scores

def calculate_fitness(schedule):
  # Implement your own fitness function here
  # This function should evaluate the quality of a schedule
  # and return a fitness score
  fitness_score = score_schedule(schedule)
  
  return fitness_score

def selection(population, fitness_scores, tournament_size = 500):
  # Implement your own selection method here
  # This function should select parents from the population
  # based on their fitness scores
  parents = []
  
  for _ in range(len(population)):
    # Randomly select individuals for the tournament
    tournament = random.sample(range(len(population)), tournament_size)
    
    # Find the individual with the highest fitness score in the tournament
    winner_index = max(tournament, key=lambda i: fitness_scores[i])
    
    # Add the winner to the parents list
    parents.append(population[winner_index])
  
  return parents

def crossover(parents):
  # Implement your own crossover method here
  # This function should create offspring schedules by
  # combining the parents' schedules
  offspring = []
  
  my_range = len(parents)
  if (my_range % 2 == 1):
    my_range -= 1  
  for i in range(0, my_range, 2):
    
    parent1 : list[Section] = parents[i]
    parent2 : list[Section] = parents[i+1]
    # TODO give score of 0 to impossible schedules
    # parent1 = [(ENES210 0101), (CMSC132 0101), (MATH141 0101), (AOSC200 0101)]
    # parent2 = [(ENES210 0102), (CMSC132 0203), (MATH141 0201), (AOSC200 0301)]
    # child1 = [(p1), (p1), (p1), (p2)]
    # child2 = [(p2), (p2), (p2), (p1)]
    
    # Randomly select the crossover point
    crossover_point = random.randint(1, len(parent1) - 1)
    
    # Create the offspring by swapping sections between parents
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    
    # Add the offspring to the list
    offspring.append(child1)
    offspring.append(child2)
    
  return offspring

def mutation(offspring, mutation_rate):
  # Implement your own mutation method here
  # This function should introduce random changes to the
  # offspring schedules based on the mutation rate
  mutated_offspring = []
    
  for schedule in offspring:
    mutated_schedule : list[Section] = schedule.copy()
    
    for section in mutated_schedule:
      # Generate a random number between 0 and 1
      random_value = random.random()
      
      if random_value < mutation_rate:
        # Replace the section with a random section
        mutated_section = get_random_section(section)
        insert_index = mutated_schedule.index(section)
        mutated_schedule.remove(section)
        mutated_schedule.insert(insert_index, mutated_section)
    
    mutated_offspring.append(mutated_schedule)
    
  return mutated_offspring

data = {}
with open("./custom_data_dump_3.json", "r") as f:
  data = json.load(f)
  
def get_random_section(section_to_replace : Section):
  random_section = random.choice(data[section_to_replace.class_name])
  
  return random_section
  

def constraint_satisfaction_problem_method(classes: list[list[Section]]):
  pass

def annealing_method(classes: list[list[Section]]):
  pass

# Original method
def sampling_based_method(classes : list[list[Section]]):
  all_schedules         = []
  conflicting_schedules = []
  
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
          section_s.weight = section_s.get_weight()
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

  return all_schedules

def process_input(class_strings : list[str], restrictions : list[str] = None):
  result = []
  classes = []
  grades  = []
  average_gpas = []
  
  data = {}
  with open("./custom_data_dump_3.json", "r") as f:
    data = json.load(f)

  for one_class in class_strings:
    # data['AASP380']
    # [{"section_num": "0101", "gpa": 3.28, "lectures": ["W 4:00pm-5:45pm", " -"], "discussions": []}, ..., {...}]
    # data['AASP380'][0]
    # {"section_num": "0101", "gpa": 3.28, "lectures": ["W 4:00pm-5:45pm", " -"], "discussions": []}
    # data['AASP380'][0]['section_num']
    # "0101"
    section_list = []
    
    for section_dict in data[one_class]:
      section_list.append(Section(section_dict, one_class))
    
    result.append(section_list)  
  
  
  # for one_class in class_strings:
  #   match one_class:
  #     # Follow their request, but warn them that they could fulfill both Gen-Eds at once
  #     case "Any":
  #       pass
  #     case 'FSAW' | 'FSAR' | 'FSMA' | 'FSOC' | 'DSHS' | 'DSHU' | "DSNS" | "DSNL" | 'DSSP' | 'DVCC' | 'DVUP' | 'SCIS':
  #       # TODO improve speed
  #       # TODO unify special + general case
  #       # --  -- #
  #       all_gen_ed_classes = UMDio.get_courses_that_fulfill_gen_ed(one_class)

  #       gen_ed_sections = []
  #       for course in all_gen_ed_classes:
  #         gen_ed_sections.extend(UMDio.get_sections(course['course_id']))
          
  #         avg_gpa, grade_dict = PlanetTerp.get_grades_from_course(course)
  #         grades.extend(grade_dict)
          
  #       average_gpas.append(avg_gpa)
          
  #       classes.append(gen_ed_sections)
  #     case _:
  #       classes.append(UMDio.get_sections(one_class))
  #       avg_gpa, grade_dict = PlanetTerp.get_grades(one_class)
  #       average_gpas.append(avg_gpa)
  #       grades.append(grade_dict)


  # for i in range(len(classes)):
  #   section_arr = []
  #   grade_dict = grades[i]

  #   for section_dict in classes[i]:
  #     # TODO maybe add check if full
  #     section_arr.append(Section(section_dict, grade_dict, average_gpas[i]))

  #   result.append(section_arr)
    
  return result
  

# JET -- CALL THIS FUNCTION FROM THE FRONT END
def get_schedules(input_classes : list[str]):
  classes = process_input(input_classes)
  all_schedules = genetic_method(classes)
  string_schedules = [[section.get_data() for section in schedule] for schedule in all_schedules]  # Array of schedules, which is an array of section objects
  
  # TODO return some sort of formatted data that works well with the 
  # calendar library
  return string_schedules


def main():
  print("Querying input from PlanetTerp and UMD.io...")
  
  # TODO query data in the background
  my_input = ["MATH141", "CMSC132", "CMSC131", "CMSC216", "COMM107", "ANTH451", "ENES210", "ENGL101"]
  # classes = process_input(my_input)
  # # string_schedules = [[str(section) for section in schedule] for schedule in classes]
  # # print(string_schedules)
  
  # # NOTE: some HNUH classes are not in PlanetTerp
  # print("Input processed!")
  
  # all_schedules = scheduling_algorithm(classes)
  # string_schedules = [[str(section) for section in schedule] for schedule in all_schedules]
  # print(string_schedules)
  schedules = get_schedules(my_input)

  with open('./schedules.txt', 'w') as convert_file:
    convert_file.write(json.dumps(schedules))
    print('Done')

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
7. Blacklist unwanted sections

# Beta version
-3. Create variants: exact (CSP), Gibbs Sampling, Genetic, Annealing
DONE- -2. Increase API call efficiency
  -1.5. Change json so that lectures are always array, add departmental GPA fallback, add restrictions
-1. Send algorithm to Professor Childs / Professor Mount to see if we can write an academic paper on it
  -0.5. Create variants: exact (CSP), Gibbs Sampling, Genetic, Annealing, Integer Linear Programming
0. Draw out front-end using wireframing software
  1.5. Add corresponding course restrictions (freshman connection, junior status etc.)
2. Add boolean to exclude full classes 
  2.5 Discuss - recommend classes to waitlist? 
3. Discuss - Only consider grade data of last 5 years (or 10 semesters)?
4. Add Machine Learning f/ determining how good a schedule is based on classes that are in it
  4.5. Maybe consider 4 day week. Maybe ask questions about what people want as inputs for ML model
5. Get all classes into program (HNUH, etc.) May need to talk to PlanetTerp or UMD.io
6. Store restrictions in Section object in score+sort, remove restricted schedules from list
  6.5. Add "x" to blacklist sections for this account (and maybe add a way to 
  remove things from blacklist later if you change your mind)
7. Choose random GenEd, or Any, or DSNS/DSHU, etc.
  7.5. Add "CMSC4" for 400 level courses
8. Add user account data (classes taken so far, fine with 8am's)

##Email to Professor:
Hello Professor Childs,
  
I am Oliver Villegas, and I was in your CMSC451 class last semester. I ran into 
a real-world problem that was reminiscent of a CMSC451 problem and I wanted to check with you
to see if my answer is correct. Here is the Problem:


### Chat GPT's Email
Subject: Seeking Your Guidance on Algorithm Solution for Real-World Problem

Dear Professor Childs,

My name is Oliver Villegas, and I was in your CMSC451 class last semester. I
write to you to ask for your guidance in evaluating an 
algorithm solution I developed for a real-world problem. The problem shares 
similarities with assignments we tackled in class, and I 
believe your guidance would greatly contribute to validating the correctness and 
efficiency of my solution.

I have attached the details of the problem along with my algorithm implementation 
for your convenience. I would greatly appreciate it if you could spare some time 
to review my work and provide your valuable feedback. Your insights and suggestions 
would be incredibly helpful in further refining my approach.

Thank you for considering my request. I eagerly await your response and the opportunity to discuss my solution with you.

Best regards,
J. Oliver Villegas


Consider the following scenario: A university counselor wants to determine the 
"best" possible schedule of 5 class sections for a student. Each class section 
s ∈ C is characterized by a professor P, an average GPA G, and a set of k class 
time ranges from s to t {(s_1, t_1), ..., (s_k, t_k)}. It is crucial to note that 
two sections with overlapping class times cannot be scheduled together. 
Furthermore, the counselor wishes to evaluate the goodness of a schedule only when 
all 5 classes are assigned. 

Question:
Design an algorithm that can assist the university counselor in solving this 
issue. Provide a detailed explanation of the algorithm, including its steps 
and any necessary data structures. Analyze the time complexity of the algorithm 
and discuss its suitability for solving the problem efficiently.



Algorithm: 
First, we assume the counselor is not concerned about obtaining the exact best 
schedule but rather a solution that is very close to the best.

schedule_options = []
Constant c times:
  running_schedule = []
  For i from 1..5:
    Randomly select the most "good" section based on an estimator function from class i that:
      - Doesn't create a schedule we've seen before
      - doesn't conflict with classes in the existing schedule 
    Add that class to the running_schedule
  Add running_schedule to schedule_options
Sort the schedules in schedule_options based on how "good" they are
Return the best 20 schedules that the alg found

Proof:


Time Complexity: O(n)


0. Problem
1. Algorithm
2. Proof of Correctness
3. Time Complexity

Thanks,
J. Oliver Villegas

# Release versions
1. ScheduleTerp (MVP) 
2. ScheduleTerp+ (Users pay $$$, All small considerations, bus route to incentivize sustainable transportation, auto-register for classes)
    2.5 UMD Sustainability fund
3. Franchise out to other universities





## Scheduling Algorithms research:
Goal: Find best algorithm for creating undergraduate student schedules, which considers
section GPA, class time, and professsor quality.
    
Genetic Algorithm for Scheduling Courses
https://link.springer.com/chapter/10.1007/978-3-662-46742-8_5

Recent developments in practical course timetabling
https://link.springer.com/chapter/10.1007/BFb0055878

A comparison of annealing techniques for academic course scheduling
https://link.springer.com/chapter/10.1007/BFb0055883

Course Scheduler and Recommendation System for Students
https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7991812
- Aside: maybe use Collaborative Filtering to 


Comparisons of Classifier Algorithms: Bayesian
Network, C4.5, Decision Forest and NBTree for
Course Registration Planning Model of
Undergraduate Students
https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4811865

"""
