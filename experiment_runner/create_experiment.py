"""Create Experiment

Usage:
  create_experiment.py <name> <file>

"""
import os
import subprocess
from datetime import datetime


def execute_shell_command(command, location):
    exit_code = subprocess.call([command], cwd=location, shell=True)
    if exit_code != 0:
        raise RuntimeError


def create_experiment_file(experiment_name, command):
    text = """#!/bin/bash
set -e
git fetch
git checkout {0}
{1}
        """.format(experiment_name, command)
    print(text)
    file_name = '{0}.pending.sh'.format(experiment_name)
    with open(file_name, 'w') as meta_file:
        meta_file.write(text)
    os.chmod(file_name, 0o770)
    return file_name


def push_experiment(workspace_location, runner_location, name, command):
    print("Experiment name: ", name)
    print("File to run: ", command)

    experiment_name = 'exp_{0}_{1}'.format(name, datetime.now().strftime("%m%d-%H%M"))
    print("Branch name: ", experiment_name)

    execute_shell_command('git checkout -b {0}'.format(experiment_name), workspace_location)
    execute_shell_command('git add .', workspace_location)
    execute_shell_command('git commit -m "Auto experiment: {0}"'.format(name), workspace_location)
    execute_shell_command('git push origin {0}'.format(experiment_name), workspace_location)

    experiment_file_name = create_experiment_file(experiment_name, command)
    os.rename(experiment_file_name, runner_location + '/experiments/' + experiment_file_name)

    execute_shell_command('git checkout master', workspace_location)
    execute_shell_command('git reset --hard {0}'.format(experiment_name), workspace_location)
    execute_shell_command('git reset HEAD~'.format(experiment_name), workspace_location)


if __name__ == '__main__':
    push_experiment('/home/sphax/Desktop/ML/Experiments/ppo', '/home/sphax/Desktop/ML/Experiments/experiment-runner', 'ce_main_test', 'python3 my_ppo.py Test FixedPosButton-v0')
