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

  def __init__(self, pf, building_map, feed_processor, map_img_name,
               loop_feed=True):
    """Initializes the displayed window and the canvas to draw with.

    Args:
      pf: a ParticleFilter object with all parameters set up. This object's
          update() function will be called every frame, and its particles will
          be used to visualize the map state.
      building_map: a BuildingMap object that contains the region definitions
          (bitmap) as well as the probabilities for each region. This will also
          be updated every frame.
      feed_processor: a FeedProcessor object that contains a classifier data
          feed from which to update the map and particle filter motion from.
      map_img_name: the name (directory path) of the background map image that
          will be displayed in the background. This must be a .gif file with the
          image of the building map.
    """
    self._pf = pf
    self._bmap = building_map
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

  def start(self):
    """Starts the update process and initializes the window's main loop.
    """
    self._update()
    self._main_window.mainloop()

  def _update(self):
    """Update the particle filter and map and render the visualizations.

    Also queues the next update after _UPDATE_INTERVAL_MS miliseconds. All
    updates happen here to all components of the particle filter program.
    """
    probabilities, turn_angle = self._feed_processor.get_next()
    if probabilities is not None:
      self._bmap.set_probabilities(probabilities)
    # Update particle filter and render everything until the next frame.
    self._pf.update(turn_angle=turn_angle)
    self._render(turn_angle)
    self._main_window.after(self._UPDATE_INTERVAL_MS, self._update)

  def _render(self, turn_angle):
    """Draws the map image and all of the particles to the screen.

    Args:
      turn_angle: the turning angle (will be displayed for visualization).
    """
    self._canvas.delete('all')
    # Draw the map.
    if self._background_img:
      self._canvas.create_image(
          0, 0, image=self._background_img, anchor='nw')
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
