import inspect


def log_error(message = 'An error happened.', terminate = False):
  callerframerecord = inspect.stack()[1]
  frame = callerframerecord[0]
  info = inspect.getframeinfo(frame)
  print 'Error logged in file {} on line {} ({}).'.format(
    info.filename, info.lineno, info.function)
  print ' >>> "{}"'.format(message)
  if terminate:
    print 'Quitting program by request of caller.'
    exit(0)


if __name__ == '__main__':
  # Test the log_error function.
  log_error('Testing log_error function.')
  log_error('Testing log_error function.', True)
