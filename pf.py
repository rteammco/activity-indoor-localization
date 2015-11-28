import math
import random

from errlog import log_error


class PFConfig(object):
  """A configuration object for the particle filter.
  
  This configuration object contains... TODO
  Populate with config file.
  """
  RANDOM_WALK_FREQUENCY = 0
  RANDOM_WALK_MAX = 0


class Particle(object):
  """A single particle.

  TODO
  """

  def __init__(self):
    self.x = 0
    self.y = 0
    self.weight = 1.0

  def randomize(self):
    self.x = random.randint(1, 100) # max map width
    self.y = random.randint(1, 100) # max map height

  def degrade(self, scale):
    """Degrades the weight of this particle by the scale.

    Args:
      scale: a number between 0 and 1 (exclusive) that will be multiplied with
          this particle's current weight to reduce its weight.
    """
    # Allow only a valid scale range. Otherwise return.
    if scale < 0 or scale > 1:
      log_error("Failed scale.")
      return
    self.weight *= scale

  def clone(self):
    """Clones this particle and returns an exact copy.

    Returns:
      An exact copy of this particle as a new object.
    """
    new_particle = Particle()
    new_particle.x = self.x
    new_particle.y = self.y
    new_particle.weight = self.weight
    return new_particle


class ParticleFilter(object):

  def __init__(self, config):
    """???

    Args:
      config: a PFConfig object containing the particle filter configuration
          values.
    """
    self._config = config
    self._particles = []
    self._max_weight = 0

  def random_walk(self):
    """Randomly offset the particles by some amount in each axis.
    
    This random walk forces the particle to "explore" new areas.
    """
    half = RANDOM_WALK_FREQUENCY / 2
    for particle in self._particles:
      dx = random.randint(0, RANDOM_WALK_MAX) - half
      dy = random.randint(0, RANDOM_WALK_MAX) - half
      particle.x += dx
      particle.y += dy

  def update_weights(self):
    """Estimate the weights of each particle based on the current map."""
    pass

  def normalize_weights(self, max_weight):
    """Normalizes the weights of all particles with respect to the given max.
    
    Makes it so that the max weight (probability) of any particle is 1.
    
    Args:
      max_weight: the maximum weight of any particle in the set.
    """
    if self.max_weight <= 0:
      return
    for particle in self._particles:
      particle.weight /= max_weight

  def resample(self):
    """Resample all particles based on probability of existing particles."""
    pass



