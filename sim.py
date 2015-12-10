import math


class FeedDataPoint():
  """An object that contains data for a single log entry of the simulation.

  This object contains data for the 
  """

  def __init__(self, region, dist_traveled, amount_turned, user_x, user_y,
      user_theta):
    """Sets the values of the next feed data point.

    Args:
      region: the region on the map that the user is currently over.
      dist_traveled: the distance moved since the last data point.
      amount_turned: the amount (in radians) that the user turned since the last
          data point.
      user_x: the ground truth x-position of the user.
      user_y: the ground truth y-position of the user.
      user_theta: the ground truth orientation of the user.
    """
    # Region and motion values:
    self._region = region
    self._odometry = dist_traveled
    self._turn = amount_turned
    # Ground truth values:
    self._ground_truth_x = user_x
    self._ground_truth_y = user_y
    self.ground_truth_theta = user_theta

  def dist_to(self, x, y):
    """Returns the distance to the other FeedDataPoint (ground truth location).

    The returned distance is rounded to the nearest whole number.

    Args:
      x: the x position of the other location.
      y: the y position of the other location.

    Returns:
      The distance between the given (x, y) location and this object's ground
      truth x and y position. Rounds to the nearest whole number.
    """
    dx = self._ground_truth_x - x
    dy = self._ground_truth_y - y
    return int(round(math.sqrt(dx * dx + dy * dy)))

  def __str__(self):
    """Returns a string representation of this object.

    Returns:
      A string contatining the data points to be written out to a feed file.
    """
    region_probs = [0] * 6 # TODO: don't hard-code 6
    region_probs[self._region - 1] = 1.0
    region_probs = ' '.join(region_probs)
    return '{}\n+ {} {}\n! {} {} {}'.format(
        region_probs, self._odometry, self._turn,
        self._ground_truth_x, self._ground_truth_y, self.ground_truth_theta)


class Simulation():
  """An object to handle simulation parameters and positioning.

  This class contains all of the simulation parameters for a user-controlled
  test environment to generate a feed file for the particle filter. All logic
  for controlling and updating the simulation is packaged in this class so that
  the UI component can just control the timing and rendering.
  """

  # Simulation parameters.
  MOVE_SPEED = 1.2
  DIST_THRESH = 30

  def __init__(self, building_map):
    """Initializes the simulation parameters and the user position

    Sets the user position to the center of the map. By default, the simulation
    is locked and the mouse is not considered as being pressed down.

    Args:
      building_map: a BuildingMap object that contains the region definitions
          and the general size of the map.
    """
    self._bmap = building_map
    self.sim_locked = True
    # Mouse state values.
    self.mouse_down = False
    self.mouse_x = 0
    self.mouse_y = 0
    # Simulated user state values.
    self.user_sim_x = self._bmap.num_cols / 2
    self.user_sim_y = self._bmap.num_rows / 2
    self.user_sim_theta = 0
    # Simulation log values.
    self._sim_logs = []

  def update(self):
    """Updates the simulation parameters based on the current user input.

    If the mouse is being held down, the user will be moved towards the mouse.
    """
    # Update user theta to direct towards the mouse.
    dx = self.mouse_x - self.user_sim_x
    dy = self.mouse_y - self.user_sim_y
    if self.mouse_down and not self.sim_locked:
      self.user_sim_theta = math.atan2(dy, dx)
    # Update user position to 'walk' towards the mouse.
    dx2 = dx * dx
    dy2 = dy * dy
    thresh2 = self.DIST_THRESH * self.DIST_THRESH
    if self.mouse_down and not self.sim_locked and (dx2 + dy2) >= thresh2:
      self.user_sim_x += self.MOVE_SPEED * math.cos(self.user_sim_theta)
      self.user_sim_y += self.MOVE_SPEED * math.sin(self.user_sim_theta)

  def _log_state(self):
    """Logs the state of the user for the current simulation step.
    
    Each log consists of the region of the map that the simulated user is
    currently over, as well as the odometry and turn information, and the
    ground truth of the user's position and orientation. The odometry data
    is the distance traveled since the last log, and the turn data is how much
    the user turned since the last log.
    """
    dist_traveled = 0
    amount_turned = 0
    region = 1 # ???
    if len(self._sim_logs) > 0:
      prev_log = self._sim_logs[-1]
      dist_traveled = prev_log.dist_to(self.user_sim_x, self.user_sim_y)
      amount_turned = prev_log.ground_truth_theta - self.user_sim_theta
    self._sim_logs.append(FeedDataPoint(region, dist_traveled, amount_turned,
        self.user_sim_x, self.user_sim_y, self.user_sim_theta))
    print str(self._sim_logs[-1])

  def button_press(self, event):
    """Event hanlder function for a mouse button press.

    Updates mouse position on left click, and moves the user to the clicked
    location on a right click (if the simulation is unlocked).

    Args:
      event: the Tk library mouse event that triggered this function call.
    """
    if event.num == 1: # left click
      self.mouse_x = event.x
      self.mouse_y = event.y
      self.mouse_down = True
    if event.num == 2 and not self.sim_locked: # right click:
      self.user_sim_x = event.x
      self.user_sim_y = event.y

  def button_release(self, event):
    """Event hanlder function for a mouse button release.

    If the left mouse button is released, sets the mose down state to False.

    Args:
      event: the Tk library mouse event that triggered this function call.
    """
    if event.num == 1: # left click
      self.mouse_down = False

  def mouse_moved(self, event):
    """Event hanlder function for a mouse movement.

    If the mouse moves while being pressed down, the mouse x and y coordinates
    are updated to the new location (effectively creating a dragging effect).

    Args:
      event: the Tk library mouse event that triggered this function call.
    """
    if self.mouse_down:
      self.mouse_x = event.x
      self.mouse_y = event.y

  def key_press(self, event):
    """Event hanlder function for a keyboard key press.

    If the escape key is pressed, the simulation lock is toggled on or off.

    Args:
      event: the Tk library keyboard event that triggered this function call.
    """
    if event.keysym == 'Escape':
      self.sim_locked = not self.sim_locked
