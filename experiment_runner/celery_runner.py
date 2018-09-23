import os
import signal
import subprocess
from functools import partial

from celery import Celery, signals, apps
from celery.exceptions import WorkerTerminate
from celery.platforms import EX_FAILURE
from celery.signals import worker_shutdown, worker_shutting_down

app = Celery('tasks', broker='pyamqp://guest@localhost//')
EXPERIMENTS_FOLDER = "./experiments/"
MAIN_TASK_ID = 'main_task'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, schedule.s(), name='Check experiments every second')


@signals.celeryd_after_setup.connect
def worker_ready(*args, **kwargs):
    try:
        apps.worker.install_worker_term_handler = partial(
            apps.worker._shutdown_handler,
            sig='SIGINT',
            how='Cold',
            exc=WorkerTerminate,
            exitcode=EX_FAILURE
        )
    except Exception as e:
        print(e)


@app.task
def schedule():
    running_experiments = [file for file in os.listdir(EXPERIMENTS_FOLDER) if file.endswith("running.sh")]
    if len(running_experiments) == 0:
        pending_experiments = [file for file in os.listdir(EXPERIMENTS_FOLDER) if file.endswith("pending.sh")]
        pending_experiments = sorted(pending_experiments, key=lambda name: os.path.getmtime(os.path.join(EXPERIMENTS_FOLDER, name)))

        if len(pending_experiments) > 0:
            file = pending_experiments[0]
            split = file.split('.')
            experiment_name = split[0]
            print('Found an experiment, running ', experiment_name)
            os.rename(EXPERIMENTS_FOLDER + file, EXPERIMENTS_FOLDER + experiment_name + ".running.sh")
            run_shell_file.apply_async(args=[experiment_name], task_id=MAIN_TASK_ID)


@app.task
def run_shell_file(experiment_name):
    script_path = os.path.abspath(EXPERIMENTS_FOLDER + experiment_name + ".running.sh")
    print('Running ', script_path)
    with open('./outputs/' + experiment_name + ".log", 'w') as output:
        process = subprocess.Popen([script_path], cwd='/home/sphax/Desktop/ML/Experiments/experiment-runner/repositories/ppo', stdout=output, stderr=output, preexec_fn=os.setsid)

    stopped = False

    def signal_handler(sig, frame):
        print('Received SIGINT, killing process')
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        os.rename(script_path, EXPERIMENTS_FOLDER + experiment_name + ".stopped.sh")
        nonlocal stopped
        stopped = True
        print('Killed process')

    signal.signal(signal.SIGTERM, signal_handler)
    process.wait()
    if process.returncode == 0:
        os.rename(script_path, EXPERIMENTS_FOLDER + experiment_name + ".finished.sh")
    elif not stopped:
        os.rename(script_path, EXPERIMENTS_FOLDER + experiment_name + ".failed.sh")


@worker_shutdown.connect
def shutdown(**kwargs):
    print("Worker shutdown")
    app.control.revoke(MAIN_TASK_ID, terminate=True, signal='SIGTERM')


@worker_shutting_down.connect
def shutting_down(**kwargs):
    print("Worker shutting down")
    app.control.revoke(MAIN_TASK_ID, terminate=True, signal='SIGTERM')
