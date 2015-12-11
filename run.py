import argparse
import math

from bmap import BuildingMap
from disp import DisplayWindow
from errlog import log_error
from feed_processor import FeedProcessor
from pf import ParticleFilter, PFConfig
from sim import Simulation


def get_pf_config(config_file=None):
  """Returns the PFConfig object.

  If no config file name is provided (or the file is malformed or otherwise
  unavailable), the default configuration values will be used instead.

  Args:
    config_file: a string containing the configuration file path. If no file
        is provided, the default values will be used instead. The config file
        should be formatted with 'KEY = value' pairs per each line, where each
        KEY matches one of the fields in the PFConfig object (e.g.
        'NUM_PARTICLES').

  Returns:
    A PFConfig object with the values, either default or from the configuration
    file.
  """
  # Initialize the default values.
  config_values = {
    'NUM_PARTICLES': 2000,
    'UPDATES_PER_FRAME': 1,
    'PARTICLE_MOVE_SPEED': 3,
    'RANDOM_WALK_FREQUENCY': 3,
    'RANDOM_WALK_MAX_DIST': 80,
    'RANDOM_WALK_MAX_THETA': math.pi / 4,
    'WEIGHT_DECAY_RATE': 1.0,
    'START_X': None,
    'START_Y': None,
    'START_THETA': None
  }
  if config_file:
    try:
      f = open(config_file, 'r')
      for line in f:
        line = line.strip()
        if line:
          line = line.split('=')
          line = map(str.strip, line)
          if len(line) == 2:
            config_values[line[0]] = eval(line[1])
    except:
      log_error('failed reading or parsing config file: {}'.format(config_file))
  config = PFConfig()
  config.NUM_PARTICLES = config_values['NUM_PARTICLES']
  config.UPDATES_PER_FRAME = config_values['UPDATES_PER_FRAME']
  config.PARTICLE_MOVE_SPEED = config_values['PARTICLE_MOVE_SPEED']
  config.RANDOM_WALK_FREQUENCY = config_values['RANDOM_WALK_FREQUENCY']
  config.RANDOM_WALK_MAX_DIST = config_values['RANDOM_WALK_MAX_DIST']
  config.RANDOM_WALK_MAX_THETA = config_values['RANDOM_WALK_MAX_THETA']
  config.WEIGHT_DECAY_RATE = config_values['WEIGHT_DECAY_RATE']
  config.START_X = config_values['START_X']
  config.START_Y = config_values['START_Y']
  config.START_THETA = config_values['START_THETA']
  return config

if __name__ == '__main__':
  """This is the main() of the program.

  Configures the particle filter and starts the display window.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--feed', dest='feed', required=True,
      help='The path for the data classifier feed file.')
  parser.add_argument(
      '--map-data', dest='map_data', required=True,
      help='The path for the map data file.')
  parser.add_argument(
      '--config', dest='config_file', required=False,
      help='Path of a configuration file.')
  parser.add_argument(
      '--map-image', dest='map_image', required=False,
      help='The path for the map image file (.gif).')
  parser.add_argument(
      '--loop-feed', dest='loop_feed', action='store_true',
      help='Set this flag to loop the input feed after it finishes.')
  parser.add_argument(
      '--make-feed', dest='make_feed', action='store_true',
      help='Set this flag to collect feed data from user control.')
  parser.add_argument(
      '--no-disp', dest='no_disp', action='store_true',
      help='Set this flag to disable visualizations (it runs faster).')
  # TODO: these noise and test params should go into a config file.
  parser.add_argument(
      '--classifier-noise', dest='c_noise', required=False, type=float,
      help='The amount of classifier noise to add to the particlefilter.')
  parser.add_argument(
      '--motion-noise', dest='m_noise', required=False, type=float,
      help='The amount of motion noise to add to the particle filter.')
  parser.add_argument(
      '--ignore-regions', dest='ignore_regions', action='store_true',
      help='Set this flag to disable using the region probabilities.')
  args = parser.parse_args()
  config = get_pf_config(args.config_file)
  building_map = BuildingMap(args.map_data)
  # If this is a feed generator run, start the user simulator.
  if args.make_feed:
    simulation = Simulation(building_map, args.feed)
    w = DisplayWindow(building_map, args.map_image, sim=simulation)
    w.start_make_feed()
  # Otherwise, run the particle filter on an existing feed.
  else:
    display_on = False if args.no_disp else True
    c_noise = args.c_noise if args.c_noise else 0
    m_noise = args.m_noise if args.m_noise else 0
    feed_processor = FeedProcessor(args.feed, args.loop_feed, c_noise, m_noise,
        ignore_regions=args.ignore_regions)
    pf = ParticleFilter(config, building_map, feed_processor)
    w = DisplayWindow(building_map, args.map_image, pf, display=display_on)
    w.start_particle_filter()
