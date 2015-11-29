import math

from bmap import BuildingMap
from disp import DisplayWindow
from pf import ParticleFilter, PFConfig


if __name__ == '__main__':
  """This is the main() of the program.

  Configures the particle filter and starts the display window.
  """
  # Configure the particle filter:
  config = PFConfig()
  config.NUM_PARTICLES = 2000
  config.UPDATES_PER_FRAME = 1
  config.PARTICLE_MOVE_SPEED = 5
  config.RANDOM_WALK_FREQUENCY = 3
  config.RANDOM_WALK_MAX_DIST = 80
  config.RANDOM_WALK_MAX_THETA = math.pi / 4
  # Start the simulation.
  print 'Starting...'
  building_map = BuildingMap('Data/map.txt')
  pf = ParticleFilter(config, building_map)
  w = DisplayWindow(pf, building_map, 'Data/test_feed.txt', 'Data/3ne.gif')
  w.start()
  print 'Goodbye!'
