import math
import time
import Tkinter as Tk

from bmap import BuildingMap
from errlog import log_error
from pf import ParticleFilter, PFConfig


class DisplayWindow():
  """The GUI window that displays all particles and controls the timers.

  This class manages displaying all particles and the map image. It also calls
  the update for the map and particle filter periodically to simulate the
  localization process.
  """

  # Display settings.
  _PARTICLE_RADIUS = 5
  _UPDATE_INTERVAL_MS = 500

  def __init__(self, pf, building_map, map_img_name):
    """Initializes the displayed window and the canvas to draw with.

    Args:
      pf: a ParticleFilter object with all parameters set up. This object's
          update() function will be called every frame, and its particles will
          be used to visualize the map state.
      building_map: a BuildingMap object that contains the region definitions
          (bitmap) as well as the probabilities for each region. This will also
          be updated every frame.
      map_img_name: the name (directory path) of the background map image that
          will be displayed in the background. This must be a .gif file with the
          image of the building map.
    """
    self._pf = pf
    self._bmap = building_map
    self._main_window = Tk.Tk()
    self._main_window.title('Particle Filter')
    self._canvas = Tk.Canvas(
        self._main_window, width=self._bmap.num_cols,
        height=self._bmap.num_rows, background='white')
    self._canvas.pack()
    # Try to load the background map image.
    try:
      self._background_img = Tk.PhotoImage(file=map_img_name)
      #self._background_label = Tk.Label(image=self._background_img)
      #self._background_label.image = self._background_img
      #self._background_label.pack()
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

    Also queues the next update after _UPDATE_INTERVAL_MS miliseconds.
    """
    self._pf.update()
    self._render()
    self._main_window.after(self._UPDATE_INTERVAL_MS, self._update)

  def _render(self):
    """Draws the map image and all of the particles to the screen.
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
      self._canvas.create_oval(x1, y1, x2, y2, fill='yellow')
      # Draw an arrow to indicate the particle's orientation.
      c_x = (x2 + x1) / 2
      c_y = (y2 + y1) / 2
      end_x = c_x + r * math.cos(particle.theta)
      end_y = c_y + r * math.sin(particle.theta)
      self._canvas.create_line(c_x, c_y, end_x, end_y, fill='yellow')


if __name__ == '__main__':
  """This is the main() of the program.

  Configures the particle filter and starts the display window.
  """
  print 'Starting...'
  config = PFConfig()
  config.NUM_PARTICLES = 1000
  config.PARTICLE_MOVE_SPEED = 5
  config.RANDOM_WALK_FREQUENCY = 5
  config.RANDOM_WALK_MAX_DIST = 40
  config.RANDOM_WALK_MAX_THETA = math.pi / 4
  building_map = BuildingMap('Data/map.txt')
  pf = ParticleFilter(config, building_map)
  w = DisplayWindow(pf, building_map, 'Data/3ne.gif')
  w.start()
  print 'Goodbye!'
