import math
import random


class Particle():
  def __init__(self):
    self.x = 0
    self.y = 0
    self.weight = 1.0

  def randomize(self):
    self.x = random.randint(1, 100) # max map width
    self.y = random.randint(1, 100) # max map height

  def degrade(self, scale):
    self.weight *= scale

  def normalize(self, max_weight):
    self.weight /= max_weight

  def clone(self):
    new_particle = Particle()
    new_particle.x = self.x
    new_particle.y = self.y
    new_particle.weight = self.weight
    return new_particle


class ParticleFilter():

  def __init__(self, floor_map):
    self.particles = []

  def random_walk(self):
    pass

  def update_weights(self):
    pass

  def normalize_weights(self):
    pass

  ;
