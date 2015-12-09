import math
import time
import Tkinter as Tk

from errlog import log_error


class DisplayWindow():
  """The GUI window that displays all particles and controls the timers.

  This class manages displaying all particles and the map image. It also calls
  the update for the map and particle filter periodically to simulate the
  localization process.
  """

  # Display settings.
  _PARTICLE_COLOR = 'yellow'
  _PARTICLE_RADIUS = 5
  _ESTIMATE_COLOR = 'purple'
  _ESTIMATE_RADIUS = 30
  _UPDATE_INTERVAL_MS = 500

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
    # Try to load the background map image.
    try:
      self._background_img = Tk.PhotoImage(file=map_img_name)
    except:
      log_error('failed to load image: {}'.format(map_img_name))
      self._background_img = None

  def start_make_feed(self):
    """
    """
    self._update_make_feed()
    self._main_window.mainloop()

  def _update_make_feed(self):
    """
    """
    print 'update make feed'
    self._render_main()
    self._main_window.after(1000, self._update_make_feed)

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
    font = ('Arial', 22)
    padding = 100
    for i in range(6):
      name = regions[i]
      prob = str(round(self._bmap.region_probs[i+1], 3))
      x = text_x - (padding * (i - 2.5))
      if i == max_index:
        color = 'yellow'
      else:
        color = 'red'
      self._canvas.create_text(x, text_y, font=font, text=name, fill=color)
      self._canvas.create_text(x, text_y + 25, font=font, text=prob, fill=color)
    if turn_angle != 0:
      turn_angle = 'TURNING: ' + str(round(turn_angle, 3))
      turn_x = text_x + padding * 4
      self._canvas.create_text(
          turn_x, text_y + 12, font=font, text=turn_angle, fill='green')
