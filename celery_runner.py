from celery import Celery
import os
import subprocess
app = Celery('tasks', broker='pyamqp://guest@localhost//')
EXPERIMENTS_FOLDER = "./experiments/"

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, schedule.s(), name='Check experiments every second')


@app.task
def schedule():    
    for file in os.listdir(EXPERIMENTS_FOLDER):
        if file.endswith("pending.sh"):
            split = file.split('.')
            experiment_name = split[0]
            print('Found an experiment, running ', experiment_name)
            os.rename(EXPERIMENTS_FOLDER + file, EXPERIMENTS_FOLDER + experiment_name + ".running.sh")
            run_shell_file.delay(experiment_name)
              
@app.task
def run_shell_file(experiment_name):
    script_path = os.path.abspath(EXPERIMENTS_FOLDER + experiment_name + ".running.sh")
    print('Running ', script_path)
    with open('./outputs/' + experiment_name + ".log", 'w') as output:  
        exit_code = subprocess.call([script_path], cwd='/mnt/bigdisk/sebastien/ailab', stdout = output, stderr=output)
    if exit_code == 0:    
        os.rename(script_path, EXPERIMENTS_FOLDER + experiment_name + ".finished.sh")
    else:
        os.rename(script_path, EXPERIMENTS_FOLDER + experiment_name + ".failed.sh")
    

