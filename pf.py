import math
import random

from errlog import log_error


class PFConfig(object):
  """A configuration object for the particle filter.
  
  This configuration object contains particle filter parameters that should be
  set up and passed to the ParticleFilter object during construction.
  """
  NUM_PARTICLES = 100
  UPDATES_PER_FRAME = 1
  PARTICLE_MOVE_SPEED = 5
  RANDOM_WALK_FREQUENCY = 5
  RANDOM_WALK_MAX_DIST = 10
  RANDOM_WALK_MAX_THETA = math.pi / 4
  WEIGHT_DECAY_RATE = 1.0
  CLUSTER_BIN_WIDTH = 10


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
    self.bin_x = 0
    self.bin_y = 0
    self.cluster_id = 0

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

  def __init__(self, config, building_map, feed_processor):
    """Initialize the particle filter parameters and all of the particles.

    All particles are initially placed in random positions.

    Args:
      config: a PFConfig object containing the particle filter configuration
          values.
      building_map: a BuildingMap object that will be referenced to update
          particle probabilities during updates.
      feed_processor: a FeedProcessor object that contains a classifier data
          feed from which to update the map and particle filter motion from.
    """
    self._config = config
    self._bmap = building_map
    self._feed_processor = feed_processor
    self.particles = []
    for i in range(self._config.NUM_PARTICLES):
      particle = Particle(self._bmap.num_cols, self._bmap.num_rows)
      self.particles.append(particle)
    self._frame = 0
    self.predicted_xs = [self._bmap.num_cols / 2]
    self.predicted_ys = [self._bmap.num_rows / 2]
    self.predicted_thetas = [0]
    self.predicted_weights = [0]
    self.best_predicted = 0
    self.ground_truth = None

  def update(self):
    """Updates the particle filter by one or more interation.

    Repeats multiple times if the given PFConfig specifies more updates per
    single frame interation. This process also sets the ground truth for the
    position if that is available from the feed processor.
    """
    probabilities, motion, ground_truth = self._feed_processor.get_next()
    move_speed, turn_angle = 0, 0
    if motion is not None:
      move_speed, turn_angle = motion[0], motion[1]
    self.ground_truth = ground_truth
    if probabilities is not None:
      self._bmap.set_probabilities(probabilities)
    for i in range(self._config.UPDATES_PER_FRAME):
      if motion is not None:
        self._move_particles(move_speed) # TODO: remove config.PARTICLE_MOVE_SPEED
        self._turn_particles(turn_angle)
      if self._config.RANDOM_WALK_FREQUENCY != 0 and (
          self._frame % self._config.RANDOM_WALK_FREQUENCY) == 0:
        self._random_walk()
      max_weight = self._update_weights()
      weight_sum = self._normalize_weights(max_weight)
      self._resample(weight_sum)
      self._estimate_location()
      self._frame += 1
    return move_speed, turn_angle

  def _move_particles(self, amount):
    """Moves all particles forward by the given amount.

    The direction of movement depends on each particle's orientation.

    Args:
      amount: the distance by which all particles will be moved forward.
    """
    for particle in self.particles:
      particle.move_by(amount)

  def _turn_particles(self, angle):
    """Updates the angle of all particles by the given amount.

    Adds or subtracts the given angle from each particle (randomly).

    Args:
      angle: the angle that will be added to or subtracted from each
          particle's theta.
    """
    for particle in self.particles:
      sign = random.randint(0, 1) * 2 - 1
      particle.theta += angle * sign

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
      weight += ((1 - weight) * (1 - self._config.WEIGHT_DECAY_RATE))
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

  def _cluster_particles(self):
    """Assigns to each particle a cluster value based on its location.

    Particles close to each other will be placed into the same cluster. The
    total number of clusters is also stored. This will set each particle's
    'cluster_id' parameter to the id of the cluster they belong to. Cluster
    IDs begin at 0.

    Returns:
      The number of clusters created.
    """
    # TODO: clean up this function.
    ######
    class ClusterBin(object):
      def __init__(self):
        self.particles = []
        self.label = -1
    ######
    def label_cluster(bins, x, y, label):
      if y < 0 or y >= len(bins) or x < 0 or len(bins) == 0 or x >= len(bins[0]):
        return
      if bins[y][x].label == -1 and len(bins[y][x].particles) > 0:
        bins[y][x].label = label
        offsets = [-1, 0, 1]
        for xo in offsets:
          for yo in offsets:
            label_cluster(bins, x + xo, y + yo, label)
    ######
    num_bin_cols = int(math.ceil(
        self._bmap.num_cols / self._config.CLUSTER_BIN_WIDTH))
    num_bin_rows = int(math.ceil(
        self._bmap.num_rows / self._config.CLUSTER_BIN_WIDTH))
    # Create the bin 2D array.
    bins = []
    for j in range(num_bin_rows):
      bins.append([])
      for i in range(num_bin_cols):
        bins[j].append(ClusterBin())
    # Assign each particle to one of the bins.
    for particle in self.particles:
      bin_x = int(particle.x) / self._config.CLUSTER_BIN_WIDTH
      bin_y = int(particle.y) / self._config.CLUSTER_BIN_WIDTH
      bin_x = min(num_bin_cols - 1, max(0, bin_x))
      bin_y = min(num_bin_rows - 1, max(0, bin_y))
      bins[bin_y][bin_x].particles.append(particle)
    # Assign each non-empty bin and all of its non-empty neighbors the same
    # label.
    next_cluster_id = 0
    for j in range(num_bin_rows):
      for i in range(num_bin_cols):
        #print '{}, {} => {}'.format(j, i, len(bins[j][i].particles))
        if bins[j][i].label == -1 and len(bins[j][i].particles) > 0:
          #print '{}, {} => {}'.format(i, j, len(bins[j][i].particles))
          label_cluster(bins, i, j, next_cluster_id)
          next_cluster_id += 1
    # Assign particles to a cluster ID based on the bin they're in.
    for row in bins:
      for cluster_bin in row:
        for particle in cluster_bin.particles:
          particle.cluster_id = cluster_bin.label
    return next_cluster_id

  def _estimate_location(self):
    """Uses the current particle to estimate the location and heading.

    The location and heading is computed as the weighted average of all
    particles.
    """
    num_clusters = self._cluster_particles()
    total_weights = [0] * num_clusters
    total_xs = [0] * num_clusters
    total_ys = [0] * num_clusters
    total_thetas = [0] * num_clusters
    for particle in self.particles:
      cluster_id = particle.cluster_id
      total_weights[cluster_id] += particle.weight
      total_xs[cluster_id] += particle.weight * particle.x
      total_ys[cluster_id] += particle.weight * particle.y
      total_thetas[cluster_id] += particle.weight * particle.theta
    self.predicted_xs = []
    self.predicted_ys = []
    self.predicted_thetas = []
    self.predicted_weights = []
    self.best_predicted = 0
    max_weight = 0
    for i in range(num_clusters):
      if total_weights[i] > max_weight:
        max_weight = total_weights[i]
        self.best_predicted = i
      self.predicted_xs.append(int(total_xs[i] / total_weights[i]))
      self.predicted_ys.append(int(total_ys[i] / total_weights[i]))
      self.predicted_thetas.append(int(total_thetas[i] / total_weights[i]))
      self.predicted_weights.append(total_weights[i])
