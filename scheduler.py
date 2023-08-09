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
import numpy as np
from typing import List
from section import Section, score_and_sort_schedules
from scheduling_algorithms.sampling_based_alg import sampling_based_method
from scheduling_algorithms.genetic_alg import genetic_method

def constraint_satisfaction_problem_method(classes: List[List[Section]]):
  pass


def process_input(class_strings : List[str], restrictions : List[str] = None):
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
    
  return result
  

# JET -- CALL THIS FUNCTION FROM THE FRONT END
def get_schedules(input_classes : List[str]):
  classes = process_input(input_classes)
  # all_schedules = genetic_method(classes)
  all_schedules = sampling_based_method(classes)
  all_schedules = score_and_sort_schedules(all_schedules)
  string_schedules = [[section.get_data() for section in schedule] for schedule in all_schedules]  # Array of schedules, which is an array of section objects
  
  # TODO return some sort of formatted data that works well with the 
  # calendar library
  return string_schedules




"""
TODO
# Alpha Version
DONE- 1. Make conflict work w/ additional days + times
DONE-  Set GPA
  DONE- 1.5. Make GPA work for multiple professors in one class
DONE- Get our input from UMD IO + PlanetTerp
DONE- Add more advanced weight selection 
6. Front-end
DONE- Blacklist unwanted sections

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
9. Clean up code library

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
