"""Create Experiment

Usage:
  create_experiment.py <name> <file>

"""
import os
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__)
    print(arguments)
    experiment_name = arguments['<name>']
    file = arguments['<file>']

    text = """#!/bin/bash
set -e
git fetch
git checkout {0}
python3 {1}
    """.format(experiment_name, file)
    print(text)
    with open('{0}.pending.sh'.format(experiment_name), 'w') as meta_file:
      meta_file.write(text)

