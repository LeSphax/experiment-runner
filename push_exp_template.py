from experiment_runner import push_experiment

from docopt import docopt

_USAGE = '''
Usage:
    exp (<label>) (<env_name>) [--debug|--load]

Options:
    --debug                        Tensorflow debugger
    --load                        Load the last save with this name

'''
options = docopt(_USAGE)

label = str(options['<label>'])
env_name = str(options['<env_name>'])
load = options['--load']


push_experiment('/home/sphax/Desktop/ML/Experiments/ppo', '/home/sphax/Desktop/ML/Experiments/experiment-runner', label, 'python3 my_ppo.py {0} {1}'.format(label, env_name))