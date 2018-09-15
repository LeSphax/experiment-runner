#!/bin/bash
celery -A celery_runner worker -B --loglevel=info