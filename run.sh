#!/bin/bash

alembic upgrade head

# Start Celery worker in the background
celery -A tasks worker -f logfile.log --loglevel=info --detach &

# # Start Celery beat in the background
celery -A tasks beat --loglevel=info --detach &

# Start your main Python script in the background
python3 app.py