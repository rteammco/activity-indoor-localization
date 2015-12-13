import random


def get_probabilities(index, num_actions, noise):
  other_prob = random.random() * noise
  main_prob = 1 - other_prob
  probs = [0] * num_actions
  probs[index] = main_prob
  while other_prob > 0:
    rand_index = random.randint(0, num_actions - 2)
    if rand_index >= index:
      rand_index += 1
    if other_prob > 0.05:
      other_prob /= 2
      rand_prob = other_prob
    else:
      rand_prob = other_prob
      other_prob = 0
    probs[rand_index] += rand_prob
  return probs

def process_request(action_command):
  action_command = action_command.strip()
  command_list = action_command.split()
  if len(command_list) == 2:
    action = command_list[0]
    count = int(command_list[1])
  else:
    action = action_command
    count = 1
  return action, count

if __name__ == '__main__':
  actions = {
      'walking': 0,
      'stairs': 1,
      'elevator': 2,
      'door': 3,
      'sitting': 4,
      'standing': 5
  }
  noise = input('Enter noise [0, 1]: ')
  if not noise or noise > 1 or noise < 0:
    print 'Noise must be between 0 and 1.'
    exit(0)
  print '\nEnter one action per line (0.5 seconds per line).\n'
  prob_list = []
  action = raw_input()
  prev_action = ''
  while action:
    # If a +, append the + angle value.
    if action.startswith('+'):
      prob_list.append(action)
    # Otherwise, randomize the probabilities normally.
    else:
      action, count = process_request(action)
      if action.lower() in actions:
        if action != prev_action:
          prob_list.append('# ' + action)
          prev_action = action
        for i in range(count):
          probs = get_probabilities(
              actions[action], len(actions), random.triangular(0, 1) * noise)
          prob_list.append(' '.join(map(str, probs)))
      else:
        print '"{}" is not a valid action.'.format(action)
    action = raw_input()
  outfile = raw_input('Output file name: ')
  if not outfile:
    print 'No output file provided. Printing.'
    for p in prob_list:
      print p
  else:
    f = open(outfile, 'w')
    for p in prob_list:
      f.write(p + '\n')
    f.close()
    print 'Wrote output to file: "{}".'.format(outfile)
