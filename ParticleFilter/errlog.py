import inspect


def log_error(message = 'An error happened.', terminate = False):
  """Prints the given message and error details.

  This function will print the given error message, and also the information
  about where that error occured, including the file name, the line, and the
  calling function.

  Args:
    message: the message from the calling function to describe the problem.
    terminate: (optional) set to True if the app should quit after this error
        is encountered.
  """
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
  """Quick test to make sure the log_error function works."""
  log_error('Testing log_error function.')
  log_error('Testing log_error function.', True)
