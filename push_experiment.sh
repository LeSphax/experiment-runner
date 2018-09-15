#!/bin/bash
set -e
echo "Experiment name: $1"
echo "File to run: $2"

experiment_name=exp_$1_`date '+%Y-%m-%dT%H-%M-%S'`
echo "Branch name: $experiment_name"
git checkout -b $experiment_name
git add .
git commit -m "Auto experiment: $1"
git push origin $experiment_name

python3 `dirname $BASH_SOURCE`/create_experiment.py $experiment_name $2
chmod 770 ${experiment_name}.pending.sh
scp ${experiment_name}.pending.sh sebastien@deadpool:/mnt/bigdisk/sebastien/experiment-runner/experiments/
rm ${experiment_name}.pending.sh

git checkout master
git reset --hard $experiment_name
git reset HEAD~


