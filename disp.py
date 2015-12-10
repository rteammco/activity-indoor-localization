import math
import time
import Tkinter as Tk

from errlog import log_error
from sim import Simulation


class DisplayWindow():
  """The GUI window that displays all particles and controls the timers.

  This class manages displaying all particles and the map image. It also calls
  the update for the map and particle filter periodically to simulate the
  localization process.
  """

  # General display settings.
  _TEXT_FONT = ('Arial', 22)
  # Display settings for particle filter.
  _PARTICLE_COLOR = 'yellow'
  _PARTICLE_RADIUS = 5
  _ESTIMATE_COLOR = 'purple'
  _ESTIMATE_RADIUS = 30
  _UPDATE_INTERVAL_MS = 500
  # Display settings for user simulation.
  _SIM_USER_COLOR = 'green'
  _SIM_USER_RADIUS = 10
  _USER_CONTROL_FPS = 30
  # Different modes for the map behavior.
  _SIM_MODE = 0
  _PF_MODE = 1

  def __init__(self, building_map, map_img_name=None, pf=None,
               feed_processor=None):
    """Initializes the displayed window and the canvas to draw with.

    Args:
      building_map: a BuildingMap object that contains the region definitions
          (bitmap) as well as the probabilities for each region. This will also
          be updated every frame.
      map_img_name: the name (directory path) of the background map image that
          will be displayed in the background. This must be a .gif file with the
          image of the building map.
      pf: a ParticleFilter object with all parameters set up. This object's
          update() function will be called every frame, and its particles will
          be used to visualize the map state.
      feed_processor: a FeedProcessor object that contains a classifier data
          feed from which to update the map and particle filter motion from.
    """
    self._bmap = building_map
    self._pf = pf
    self._feed_processor = feed_processor
    self._main_window = Tk.Tk()
    self._main_window.title('Particle Filter')
    self._canvas = Tk.Canvas(
        self._main_window, width=self._bmap.num_cols,
        height=self._bmap.num_rows, background='white')
    self._canvas.pack()
    # Set up the simulation if the particle filter is not available.
    self._sim = None
    if not self._pf:
      self._sim = Simulation(self._bmap.num_cols, self._bmap.num_rows)
    # Try to load the background map image.
    try:
      self._background_img = Tk.PhotoImage(file=map_img_name)
    except:
      log_error('failed to load image: {}'.format(map_img_name))
      self._background_img = None
    self._mode = self._SIM_MODE if self._sim else self._PF_MODE

  def start_make_feed(self):
    """Starts the use-controlled simulation to generate a feed file.

    Binds user inputs and starts the UI loop. If the simulation object is not
    available, this function will log a fatal error.
    """
    if not self._sim:
      log_error(
        'could not start sim: Simulation object missing.', terminate=True)
      return
    self._main_window.bind('<KeyPress>', self._sim.key_press)
    self._main_window.bind('<Button>', self._sim.button_press)
    self._main_window.bind('<ButtonRelease>', self._sim.button_release)
    self._main_window.bind('<Motion>', self._sim.mouse_moved)
    self._update_make_feed()
    self._main_window.mainloop()

  def _update_make_feed(self):
    """Updates the Simulation object and renders the simulation.
    """
    self._sim.update()
    self._render_main()
    self._render_user_sim()
    self._main_window.after(1000/self._USER_CONTROL_FPS, self._update_make_feed)

  def start_particle_filter(self):
    """Starts the update process and initializes the window's main loop.

    This action will start the particle filter simulation. For this case, the
    particle filter, map object, and processor feed must not be None.
    """
    if self._pf is None or self._bmap is None or self._feed_processor is None:
      log_error('cannot start updating particle filter', terminate=True)
      return
    self._update_particle_filter()
    self._main_window.mainloop()

  def _update_particle_filter(self):
    """Update the particle filter and map and render the visualizations.

    Also queues the next update after _UPDATE_INTERVAL_MS miliseconds. All
    updates happen here to all components of the particle filter program.
    """
    probabilities, turn_angle = self._feed_processor.get_next()
    if probabilities is not None:
      self._bmap.set_probabilities(probabilities)
    # Update particle filter and render everything until the next frame.
    self._pf.update(turn_angle=turn_angle)
    self._render_main()
    self._render_particles(turn_angle)
    self._main_window.after(
        self._UPDATE_INTERVAL_MS, self._update_particle_filter)

  def _render_main(self):
    """Clears the screen and draws the map image.

    This method should be called before rendering anything else.
    """
    self._canvas.delete('all')
    # Draw the map.
    if self._background_img:
      self._canvas.create_image(
          0, 0, image=self._background_img, anchor='nw')
    if self._mode == self._SIM_MODE:
      mode_text = 'Simulation Mode'
    else:
      mode_text = 'Particle Filter Mode'
    text_y = 40
    text_x = self._bmap.num_cols / 2
    self._canvas.create_text(
        text_x, text_y, font=self._TEXT_FONT, text=mode_text, fill='blue')

  def _render_user_sim(self):
    """Renders the simulation component to the screen.

    This includes the simulated user and the mouse dragging line.
    """
    # Draw the user's position and orientation.
    x1 = self._sim.user_sim_x - self._SIM_USER_RADIUS
    y1 = self._sim.user_sim_y - self._SIM_USER_RADIUS
    r2 = 2 * self._SIM_USER_RADIUS
    x2 = x1 + r2
    y2 = y1 + r2
    self._canvas.create_oval(x1, y1, x2, y2, fill=self._SIM_USER_COLOR)
    end_x = self._sim.user_sim_x + r2 * math.cos(self._sim.user_sim_theta)
    end_y = self._sim.user_sim_y + r2 * math.sin(self._sim.user_sim_theta)
    self._canvas.create_line(
        self._sim.user_sim_x, self._sim.user_sim_y, end_x, end_y, width=4,
        fill=self._SIM_USER_COLOR)
    # Draw a circle around the user to indicate the mouse activity distance.
    x1 = self._sim.user_sim_x - self._sim.DIST_THRESH
    y1 = self._sim.user_sim_y - self._sim.DIST_THRESH
    r2 = 2 * self._sim.DIST_THRESH
    x2 = x1 + r2
    y2 = y1 + r2
    # TODO: some of the colors can be moved up as global variables.
    self._canvas.create_oval(x1, y1, x2, y2, outline='red')
    # Draw a line from the user to the mouse if the mouse is pressed
    if self._sim.mouse_down:
      self._canvas.create_line(
          self._sim.user_sim_x, self._sim.user_sim_y, self._sim.mouse_x,
          self._sim.mouse_y, fill='yellow')
    # Draw the text to display all pressed movement keys.
    text_y = self._bmap.num_rows - 50
    text_x = self._bmap.num_cols / 2
    if not self._sim.sim_locked:
      if self._sim.mouse_down:
        self._canvas.create_text(
            text_x, text_y, font=self._TEXT_FONT, text='Logging', fill='blue')
    else:
      locked_text = 'Simulation locked. Press ESC to unlock.'
      self._canvas.create_text(
          text_x, text_y, font=self._TEXT_FONT, text=locked_text, fill='red')

  def _render_particles(self, turn_angle):
    """Draws the particles and info from the particle filter to the screen.

    This should only be called if the particle filter is defined.

    Args:
      turn_angle: the turning angle (will be displayed for visualization).
    """
    if not self._pf:
      log_error('cannot render particle filter: variable _pf not defined.')
      return
    # Draw the particles.
    for particle in self._pf.particles:
      # Scale radius based on probability for visualization.
      r = self._PARTICLE_RADIUS
      extra_r = (self._PARTICLE_RADIUS * particle.weight) / 2
      r = r + extra_r
      # Draw a dot at the particle's position.
      x1 = particle.x - r / 2
      y1 = particle.y - r / 2
      x2 = x1 + r
      y2 = y1 + r
      self._canvas.create_oval(x1, y1, x2, y2, fill=self._PARTICLE_COLOR)
      # Draw an arrow to indicate the particle's orientation.
      c_x = (x2 + x1) / 2
      c_y = (y2 + y1) / 2
      end_x = c_x + r * math.cos(particle.theta)
      end_y = c_y + r * math.sin(particle.theta)
      self._canvas.create_line(
          c_x, c_y, end_x, end_y, fill=self._PARTICLE_COLOR)
    # Draw the particle filter's estimated location.
    half_r = self._ESTIMATE_RADIUS / 2
    thickness = self._ESTIMATE_RADIUS / 8 + 1
    self._canvas.create_oval(
        self._pf.predicted_x-half_r, self._pf.predicted_y-half_r,
        self._pf.predicted_x+half_r, self._pf.predicted_y+half_r,
        outline=self._ESTIMATE_COLOR, width=thickness)
    # Draw the estimated orientation over the estimated location.
    costheta = math.cos(self._pf.predicted_theta)
    sintheta = math.sin(self._pf.predicted_theta)
    start_x = self._pf.predicted_x + half_r * costheta
    start_y = self._pf.predicted_y + half_r * sintheta
    end_x = start_x + self._ESTIMATE_RADIUS * costheta
    end_y = start_y + self._ESTIMATE_RADIUS * sintheta
    self._canvas.create_line(
        start_x, start_y, end_x, end_y,
        fill=self._ESTIMATE_COLOR, width=thickness)
    # Draw the probabilities and current max estimate.
    # TODO: don't hard-code the locations here!
    text_y = self._bmap.num_rows - 50
    text_x = self._bmap.num_cols / 2
    max_index = self._bmap.region_probs.index(max(self._bmap.region_probs)) - 1
    regions = ['hall', 'stairs', 'elevator', 'door', 'sit', 'stand']
    padding = 100
    for i in range(6):
      name = regions[i]
      prob = str(round(self._bmap.region_probs[i+1], 3))
      x = text_x - (padding * (i - 2.5))
      if i == max_index:
        color = 'yellow'
      else:
        color = 'red'
      self._canvas.create_text(
          x, text_y, font=self._TEXT_FONT, text=name, fill=color)
      self._canvas.create_text(
          x, text_y + 25, font=self._TEXT_FONT, text=prob, fill=color)
    if turn_angle != 0:
      turn_angle = 'TURNING: ' + str(round(turn_angle, 3))
      turn_x = text_x + padding * 4
      self._canvas.create_text(
          turn_x, text_y + 12, font=font, text=turn_angle, fill='green')
