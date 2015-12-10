import math


class Simulation():
  """An object to handle simulation parameters and positioning.

  This class contains all of the simulation parameters for a user-controlled
  test environment to generate a feed file for the particle filter. All logic
  for controlling and updating the simulation is packaged in this class so that
  the UI component can just control the timing and rendering.
  """

  def __init__(self, map_width, map_height):
    """Initializes the simulation parameters and the user position

    Sets the user position to the center of the map. By default, the simulation
    is locked and the mouse is not considered as being pressed down.

    Args:
      map_width: (int) the width of the simulation map.
      map_height: (int) the height of the simulation map.
    """
    self._user_radius = 10
    self._move_speed = 1.2
    self._distance_thresh = 30
    self.sim_locked = True
    # Mouse state values.
    self.mouse_down = False
    self.mouse_x = 0
    self.mouse_y = 0
    # Simulated user state values.
    self.user_sim_x = map_width / 2
    self.user_sim_y = map_height / 2
    self.user_sim_theta = 0

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
    thresh2 = self._distance_thresh * self._distance_thresh
    if self.mouse_down and not self.sim_locked and (dx2 + dy2) >= thresh2:
      self.user_sim_x += self._move_speed * math.cos(self.user_sim_theta)
      self.user_sim_y += self._move_speed * math.sin(self.user_sim_theta)

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
