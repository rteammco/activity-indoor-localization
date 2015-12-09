import argparse
import math

from bmap import BuildingMap
from disp import DisplayWindow
from errlog import log_error
from feed_processor import FeedProcessor
from pf import ParticleFilter, PFConfig


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
    'WEIGHT_DECAY_RATE': 1.0
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
  args = parser.parse_args()
  config = get_pf_config(args.config_file)
  # Start the simulation.
  building_map = BuildingMap(args.map_data)
  if args.make_feed:
    w = DisplayWindow(building_map, args.map_image)
    w.start_make_feed()
  else:
    pf = ParticleFilter(config, building_map)
    feed_processor = FeedProcessor(args.feed, args.loop_feed)
    w = DisplayWindow(
        building_map, args.map_image, pf, feed_processor)
    w.start_particle_filter()
