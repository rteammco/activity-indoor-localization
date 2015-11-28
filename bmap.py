from errlog import log_error


class BuildingMap():

  NUMBER_OF_REGIONS = 3
  VOID_SPACE = 0
  HALLWAY = 1
  STAIRCASE = 2

  def __init__(self, map_file_name):
    try:
      map_file = open(map_file_name, 'r')
      self._map_data = map_file.readlines()
    except:
      self._map_data = []
      log_error('failed reading file: {}'.format(map_file_name))
    # Process the map data into a 2D grid.
    self.num_rows = len(self._map_data)
    for i in range(len(self._map_data)):
      row = self._map_data[i].strip()
      row = row.split(',')
      self._map_data[i] = map(int, row)
    self.num_cols = len(self._map_data[0]) if self.num_rows > 0 else 0
    # Initialize all region probabilities to 1 (except void space).
    self._region_probs = [1.0] * self.NUMBER_OF_REGIONS
    self._region_probs[self.VOID_SPACE] = 0.01

  def probability_of(self, x, y):
    """Returns the probability at region x, y.
    """
    if x < 0 or x >= self.num_cols or y < 0 or y >= self.num_rows:
      return 0
    region = self._map_data[y][x]
#    prob = self._region_probs[region]
#    if region == 0:
#      print '@ region 0, prob = {}'.format(prob)
    return self._region_probs[region]

  def set_probabilities(self, prob_map):
    """Sets the probabilities of each region."""
    pass


if __name__ == '__main__':
  """Quick test for the BuildingMap object to make sure it works."""
  m = BuildingMap('Data/map.txt')
  print m.num_rows
  print m.num_cols
  m = BuildingMap('Data/bad_file_name.txt')
  print m.num_rows
  print m.num_cols
