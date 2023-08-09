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

def schedule_terp(input, is_dev = True):
  # print("Querying input from PlanetTerp and UMD.io...")

  # TODO query data in the background
  # example input: ["CMSC132", "MATH141", "ENGL101"]
  my_input = input

  # NOTE: some HNUH classes are not in PlanetTerp

  schedules = get_schedules(my_input)

  if is_dev:
    with open('./schedules.txt', 'w') as convert_file:
      convert_file.write(json.dumps(schedules))
    # print('Done')

  return schedules
  
def lambda_handler(event, context):
  courses = []
  response =  {
    "isBase64Encoded": True,
    "statusCode": 200,
  }
  if 'queryStringParameters' in event:
    courses = event['queryStringParameters']['courses'].split(',')
  else:
    courses = event['courses']
  response['body'] =str(main(courses=courses, is_dev=False))  # This is called by an AWS Lambda function.
  return response

def main(courses=["ENES210", "CMSC351", "CMSC330"], is_dev=True):
  string_schedules = schedule_terp(courses, is_dev)
  if is_dev:
    print(string_schedules)
  return string_schedules

if __name__ == '__main__':
  main()
