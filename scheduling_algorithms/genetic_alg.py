#!/usr/bin/env python3
"""Genetic algorithm for finding optimal college schedules.
"""
__author__     = "Oliver Villegas, Jaxon Lee"
__copyright__  = "Copyright 2023"
__credits__    = ["Jet Lee"]
__license__    = "MIT"
__version__    = "0.1.0"
__maintainer__ = "Oliver Villegas, Jaxon Lee"
__email__      = "j.oliver.vv@gmail.com, jaxondlee@gmail.com"
__status__     = "Development"

from section import Section, score_schedule
from .sampling_based_alg import sampling_based_method
import random
import json

data = {}
with open("./custom_data_dump_3.json", "r") as f:
  data = json.load(f)
  
def get_random_section(section_to_replace : Section):
  random_section = Section(random.choice(data[section_to_replace.class_name]), section_to_replace.class_name)
  
  return random_section


def genetic_method(classes: list[list[Section]]):
  """_summary_

  Args:
      classes (list[list[Section]]): _description_

  Returns:
      _type_: _description_
  """
  POPULATION_SIZE = 100
  GENERATIONS = 10
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
      print("Generation: ", generation)
  
  # Sort the final population by fitness
  population.sort(key=lambda x: evaluate_fitness([x])[0], reverse=True)
  
  # Return the schedules from the final population
  return population

def generate_initial_population(classes, population_size):
  """_summary_

  Args:
      population (list[list[Section]]): _description_

  Returns:
      _type_: _description_
  """
  # TODO add functionality for population size
  population = sampling_based_method(classes)
  
  population = [list(schedule) for schedule in population]
  
  return population

def evaluate_fitness(population : list[list[Section]]):
  """_summary_

  Args:
      population (list[list[Section]]): _description_

  Returns:
      _type_: _description_
  """
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
