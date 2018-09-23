#!/bin/bash
celery -A experiment_runner.celery_runner worker -B --loglevel=info