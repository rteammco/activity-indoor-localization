import math
import random

from errlog import log_error


class PFConfig(object):
  """A configuration object for the particle filter.
  
  This configuration object contains... TODO
  Populate with config file.
  """
  NUM_PARTICLES = 100
  RANDOM_WALK_FREQUENCY = 5
  RANDOM_WALK_MAX = 10
  WINDOW_WIDTH = 100
  WINDOW_HEIGHT = 100


class Particle(object):
  """A single particle.

  TODO
  """

  def __init__(self):
    self.x = 0
    self.y = 0
    self.weight = 1.0

  def randomize(self):
    self.x = random.randint(1, 500) # max map width
    self.y = random.randint(1, 500) # max map height

  def degrade(self, scale):
    """Degrades the weight of this particle by the scale.

    Args:
      scale: a number between 0 and 1 (exclusive) that will be multiplied with
          this particle's current weight to reduce its weight.
    """
    # Allow only a valid scale range. Otherwise return.
    if scale < 0 or scale > 1:
      log_error('scale = {} is invalid'.format(scale))
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
  """ TODO
  """

  def __init__(self, config):
    """???

    Args:
      config: a PFConfig object containing the particle filter configuration
          values.
    """
    self._config = config
    self.particles = []
    for i in range(self._config.NUM_PARTICLES):
      particle = Particle()
      particle.randomize() # TODO: randomize with respect to the map!
      self.particles.append(particle)
    self._frame = 0

  def update(self):
    """Updates the particle filter by one interation.
    """
    # TODO: update agent movement.
    if self._config.RANDOM_WALK_FREQUENCY != 0 and (
        self._frame % self._config.RANDOM_WALK_FREQUENCY) == 0:
      self._random_walk()
    max_weight = self._update_weights()
    weight_sum = self._normalize_weights(max_weight)
    self._resample(weight_sum)
    self._frame += 1

  def _random_walk(self):
    """Randomly offset the particles by some amount in each axis.
    
    This random walk forces the particle to "explore" new areas.
    """
    half = self._config.RANDOM_WALK_MAX / 2
    for particle in self.particles:
      dx = random.randint(0, self._config.RANDOM_WALK_MAX) - half
      dy = random.randint(0, self._config.RANDOM_WALK_MAX) - half
      particle.x += dx
      particle.y += dy

  def _update_weights(self):
    """Estimate the weights of each particle based on the current map.

    Returns:
      The maximum weight of all particles.
    """
    max_weight = 1
    return max_weight

  def _normalize_weights(self, max_weight):
    """Normalizes the weights of all particles with respect to the given max.
    
    Makes it so that the max weight (probability) of any particle is 1.
    
    Args:
      max_weight: the maximum weight of any particle in the set.

    Returns:
      The sum of all of the normalized particle weights.
    """
    if max_weight <= 0:
      log_error('max_weight = {} is invalid'.format(max_weight))
      return 0
    weight_sum = 0
    for particle in self.particles:
      particle.weight /= max_weight
      weight_sum += particle.weight
    return weight_sum

  def _resample(self, weight_sum):
    """Resample all particles based on probability of existing particles.
    
    Updates the particles array to the new set of resampled particles.

    Args:
      weight_sum: the sum of all particle weights.
    """
    new_particles = []
    for particle in self.particles:
      index = 0
      selection = self.particles[index]
      weight_pos = (random.random() * weight_sum) - selection.weight
      while weight_pos > 0:
        index += 1
        selection = self.particles[index]
        weight_pos -= selection.weight
      new_particles.append(selection.clone())
    self.particles = new_particles
