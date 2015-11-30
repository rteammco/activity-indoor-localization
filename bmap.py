from errlog import log_error


class BuildingMap():
  """This class contains the bitmap data for the building map.
  """

  # Region defintions by ID (this must be the same as in the file).
  NUMBER_OF_REGIONS = 7
  VOID_SPACE = 0
  HALLWAY = 1
  STAIRCASE = 2
  ELEVATOR = 3
  DOOR = 4
  SITTING_AREA = 5
  STANDING_AREA = 6

  def __init__(self, map_file_name):
    """Reads the given file and formats the data for the bitmap.

    Args:
      map_file_name: the name of the text file containing all of the bitmap
          data. This file should be have newline-delimited rows and
          comma-delimited columns. Each "pixel" in the original map image should
          have a corresponding bitmap value to indicate what type of region it
          is in this file.
    """
    try:
      map_file = open(map_file_name, 'r')
      self._map_data = map_file.readlines()
    except:
      self._map_data = []
      log_error('failed reading file: {}'.format(map_file_name), terminate=True)
    # Process the map data into a 2D grid.
    self.num_rows = len(self._map_data)
    for i in range(len(self._map_data)):
      row = self._map_data[i].strip()
      row = row.split(',')
      self._map_data[i] = map(int, row)
    self.num_cols = len(self._map_data[0]) if self.num_rows > 0 else 0
    # Initialize all region probabilities to 1 (except void space).
    self.region_probs = [1.0] * self.NUMBER_OF_REGIONS
    self.region_probs[self.VOID_SPACE] = 0.0

  def probability_of(self, x, y):
    """Returns the probability at region x, y.

    Args:
      x: the (int) pixel x-position (col).
      y: the (int) pixel y-position (row).

    Returns:
      The probability of the region that this position is covering. If the
      given coordinates are out of range of the map's dimensions, returns 0
      as the probability.
    """
    if x < 0 or x >= self.num_cols or y < 0 or y >= self.num_rows:
      return 0
    region = self._map_data[y][x]
    return self.region_probs[region]

  def set_probabilities(self, probabilities):
    """Sets the probabilities of each region.

    Args:
      probabilities: the probability weights for each of the classes. This
          should be a list of NUMBER_OF_REGIONS-1 values between 0 and 1, and
          ideally the total sum of these values should equal to 1. Do not pass
          in the probability of the void region (assumed to always be 0).
    """
    if len(probabilities) != (self.NUMBER_OF_REGIONS - 1):
      log_error('given number of probabilities does not equal {}'.format(
          self.NUMBER_OF_REGIONS - 1))
      return
    for i in range(1, self.NUMBER_OF_REGIONS):
      self.region_probs[i] = probabilities[i-1]


if __name__ == '__main__':
  """Quick test for the BuildingMap object to make sure it works."""
  m = BuildingMap('Data/map.txt')
  print m.num_rows
  print m.num_cols
  m = BuildingMap('Data/bad_file_name.txt')
  print m.num_rows
  print m.num_cols
