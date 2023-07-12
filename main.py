#!/usr/bin/env python3
"""ScheduleTerp driver. This actually runs the algorithm.
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
from scheduler import get_schedules

def schedule_terp(input):
  # print("Querying input from PlanetTerp and UMD.io...")

  # TODO query data in the background
  # example input: ["CMSC132", "MATH141", "ENGL101"]
  my_input = input

  # NOTE: some HNUH classes are not in PlanetTerp


  schedules = get_schedules(my_input)

  with open('./schedules.txt', 'w') as convert_file:
    convert_file.write(json.dumps(schedules))
    # print('Done')

  return schedules
  

def main():
  test_classes = ["ENES210", "CMSC351", "CMSC330"]
  string_schedules = schedule_terp(test_classes)
  print(string_schedules)

if __name__ == '__main__':
  main()
