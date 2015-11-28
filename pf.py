import math
import random

from errlog import log_error


class PFConfig(object):
  """A configuration object for the particle filter.
  
  This configuration object contains particle filter parameters that should be
  set up and passed to the ParticleFilter object during construction.
  """
  NUM_PARTICLES = 100
  PARTICLE_MOVE_SPEED = 5
  RANDOM_WALK_FREQUENCY = 5
  RANDOM_WALK_MAX_DIST = 10
  RANDOM_WALK_MAX_THETA = math.pi / 4


class Particle(object):
  """A single particle.

  Initializes at a random position and orientation, and adds functionality to
  move along its oriented direction, and the ability to clone itself for the
  particle filter.
  """

  def __init__(self, map_width=10, map_height=10):
    """Initializes a new, randomly positioned particle with weight = 1.

    Pass in the parameters for the map width and height to randomly position
    the particle somewhere on the map. No need to pass in these parameters when
    cloning the particle, since the cloned copy will get the same values.

    Args:
      map_width: (optional) the width of the map being used.
      map_height: (optional) the height of the map being used.
    """
    self.x = random.randint(1, map_width)
    self.y = random.randint(1, map_height)
    self.theta = random.random() * 2 * math.pi
    self.weight = 1.0

  def move_by(self, amount):
    """Moves the particle by the given amount in its oriented direction.

    Args:
      amount: the amount that the particle will be moved by.
    """
    self.x += amount * math.cos(self.theta)
    self.y += amount * math.sin(self.theta)

  def clone(self):
    """Clones this particle and returns an exact copy.

    Returns:
      An exact copy of this particle as a new object.
    """
    new_particle = Particle()
    new_particle.x = self.x
    new_particle.y = self.y
    new_particle.theta = self.theta
    new_particle.weight = self.weight
    return new_particle


class ParticleFilter(object):
  """ The particle filter implementation for the map.

  Provides basic particle filter functionality by moving particles, resampling,
  updaing their positions, and setting their probabilities based on the current
  map state.
  """

  def __init__(self, config, building_map):
    """Initialize the particle filter parameters and all of the particles.

    All particles are initially placed in random positions.

    Args:
      config: a PFConfig object containing the particle filter configuration
          values.
      building_map: a BuildingMap object that will be referenced to update
          particle probabilities during updates.
    """
    self._config = config
    self._bmap = building_map
    self.particles = []
    for i in range(self._config.NUM_PARTICLES):
      particle = Particle(self._bmap.num_cols, self._bmap.num_rows)
      self.particles.append(particle)
    self._frame = 0
    self.predicted_x = self._bmap.num_cols / 2
    self.predicted_y = self._bmap.num_rows / 2
    self.predicted_theta = 0

  def update(self):
    """Updates the particle filter by one interation.
    """
    if True: # TODO: only move particles if user is supposedly moving!
      self._move_particles(self._config.PARTICLE_MOVE_SPEED)
    # TODO: if the user "turn" is detected, add that here too!
    if self._config.RANDOM_WALK_FREQUENCY != 0 and (
        self._frame % self._config.RANDOM_WALK_FREQUENCY) == 0:
      self._random_walk()
    max_weight = self._update_weights()
    weight_sum = self._normalize_weights(max_weight)
    self._resample(weight_sum)
    self._estimate_location()
    self._frame += 1

  def _move_particles(self, amount):
    """Moves all particles forward by the given amount.

    The direction of movement depends on each particle's orientation.
    """
    for particle in self.particles:
      particle.move_by(amount)

  def _random_walk(self):
    """Randomly offset the particles by some amount in each axis.
    
    This random walk forces the particle to "explore" new areas.
    """
    half_dist = self._config.RANDOM_WALK_MAX_DIST / 2
    half_theta = self._config.RANDOM_WALK_MAX_THETA / 2
    for particle in self.particles:
      dx = random.randint(0, self._config.RANDOM_WALK_MAX_DIST) - half_dist
      dy = random.randint(0, self._config.RANDOM_WALK_MAX_DIST) - half_dist
      dtheta = random.random() * self._config.RANDOM_WALK_MAX_THETA - half_theta
      particle.x += dx
      particle.y += dy
      particle.theta += dtheta

  def _update_weights(self):
    """Estimate the weights of each particle based on the current map.

    Returns:
      The maximum weight of all particles.
    """
    max_weight = 0
    for particle in self.particles:
      weight = self._bmap.probability_of(int(particle.x), int(particle.y))
      particle.weight *= weight
      max_weight = max(max_weight, weight)
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

  def _estimate_location(self):
    """Uses the current particle to estimate the location and heading.

    The location and heading is computed as the weighted average of all
    particles.
    """
    # TODO: we should also do some connected-components clustering to make the
    # particles predict more than 1 location where applicable.
    total_weight = 0
    total_x = 0
    total_y = 0
    total_theta = 0
    for particle in self.particles:
      total_weight += particle.weight
      total_x += particle.weight * particle.x
      total_y += particle.weight * particle.y
      total_theta += particle.weight * particle.theta
    self.predicted_x = int(total_x / total_weight)
    self.predicted_y = int(total_y / total_weight)
    self.predicted_theta = total_theta / total_weight

