import sys


def throw_error(error_message):
    sys.stderr.write('ERROR: {0}\n'.format(error_message))
    sys.exit(1)
