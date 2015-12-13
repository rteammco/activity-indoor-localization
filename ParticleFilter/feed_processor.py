import math
import random

from errlog import log_error


class FeedProcessor(object):
  """Processes a classifier feed data file to provide easy updates.
  """

  def __init__(self, feed_file_name, loop_feed=True, classifier_noise=0.0,
      motion_noise=0.0, ignore_regions=False):
    """Reads the given filename and tries to parse the classifier feed.
    
    Args:
      feed_file_name: the name of the file that contains all probabilities for
          each of the activities. Empty lines or lines starting with '#' will be
          ignored. All other lines should have a series of space-delimited
          probability values, one for each region class, in the same order as
          defined in the BuildingMap class. A line can also start with a '+', in
          which case the turn angle for the step associated with the
          probabilities of the line above it will be updated.
      loop_feed: (optional) set to False if this feed shouldn't loop around.
          Otherwise, when the data stream runs out, it will loop from the
          beginning.
      classifier_noise: added noise of the classifier between 0 and 1. A higher
          value means more random noise.
      motion_noise: the added noise of the odometry and turn rate. A higher
          value means more random noise.
      ignore_regions: set to true to ignore region probabilities (set them all
          to be equal) and only update based on motion data. This is useful for
          comparing with an odometry-and-turn-only method.
    """
    self._probability_list = []
    self._motions = []
    self._ground_truths = []
    self._loop_feed = loop_feed
    self._classifier_noise = classifier_noise
    self._motion_noise = motion_noise
    try:
      f = open(feed_file_name, 'r')
      for line in f:
        line = line.strip()
        # Skip empty or commented lines.
        if len(line) == 0 or line.startswith('#'):
          continue
        # If line begins with a '+', that means it's odometry and a turn angle,
        # so add those values to the previous position.
        if line.startswith('+'):
          line = line[1:]
          line = line.split()
          if len(line) >= 2:
            motion = int(line[0]), float(line[1])
            if len(self._motions) > 0:
              self._motions[-1] = motion
        # If line begins with a '!', that means it's ground truth information,
        # so add that information to the previous position.
        elif line.startswith('!'):
          line = line[1:]
          line = line.split()
          if len(line) >= 3:
            ground_truth = int(line[0]), int(line[1]), float(line[2])
            if len(self._ground_truths) > 0:
              self._ground_truths[-1] = ground_truth
        # Otherwise add the probabilities and initialize the motion and ground
        # truth values at that point to None.
        else:
          line = line.split()
          if ignore_regions:
            count = len(line)
            self._probability_list.append([1.0 / count] * count)
          else:
            self._probability_list.append(map(float, line))
          self._motions.append(None)
          self._ground_truths.append(None)
    except:
      log_error('failed to load feed file: {}'.format(feed_file_name))
    self._next_index = 0
    self._num_feeds = len(self._probability_list)

  def has_next(self):
    """Returns True if there is an available feed in the stream.

    Returns:
      True if there is another entree in the feed, False otherwise. If looping
      is enabled, this should always return True if there is at least one feed
      entry.
    """
    return self._num_feeds > self._next_index

  def get_next(self):
    """Returns the next feed probabilities and turn angle.

    Use has_next() to ensure that this returns a valid list of probabilities.

    Returns:
      A tuple (probabilities, turn_angle) where the probabilities is a list of
      the map region probabilities for the next iteration, and turn_angle is
      the angle by which the user is supposedly turning for the next iteration.
      If there is no more data in the stream and looping is turned off, probs
      will be None and turn_angle will be 0.
    """
    if self._num_feeds > self._next_index:
      probs = self._probability_list[self._next_index]
      if self._classifier_noise > 0:
        probs = self._add_classifier_noise(probs, self._classifier_noise)
      motion = self._motions[self._next_index]
      if self._motion_noise > 0:
        motion = self._add_motion_noise(motion, self._motion_noise)
      ground_truth = self._ground_truths[self._next_index]
      self._next_index += 1
      # If index is out of bounds, reset if we are looping the classifier feed.
      if self._next_index >= self._num_feeds and self._loop_feed:
        self._next_index = 0
      return probs, motion, ground_truth
    else:
      return None, None, None

  def _add_motion_noise(self, motion, motion_noise):
    # TODO comments
    if motion is None:
      return None
    move_speed, turn_speed = motion
    # Add noise to the odometry.
    noise = random.random() * motion_noise
    move_noise = random.choice([1, -1]) * noise * move_speed
    move_speed = move_speed + move_noise
    # Add noise to the turning rate.
    noise = random.random() * motion_noise
    turn_noise = random.choice([1, -1]) * noise * math.pi / 2
    turn_speed = turn_speed + turn_noise
    # Return the noisy values.
    return move_speed, turn_speed

  def _add_classifier_noise(self, region_probs, classifier_noise):
    """Adds random classifier noise to the given probabilities.
    """
    # TODO comments
    # Add random noise to the region probabilities.
    for i in range(len(region_probs)):
      noise = abs(random.normalvariate(0, classifier_noise))
      if region_probs[i] == 1: # if this is the highest, subtract. TODO: max?
        region_probs[i] = abs(region_probs[i] - noise)
      else:
        region_probs[i] += noise
    # Normalize the noisy vector.
    norm = 0
    for prob in region_probs:
      norm += prob * prob
    norm = math.sqrt(norm)
    for i in range(len(region_probs)):
      region_probs[i] /= norm
    return region_probs
