#!/bin/bash

alembic upgrade head

nohup rq worker &

# Start scheduler.py in the background
nohup python3 utils/scheduler/scheduler.py &

# Start your main Python script in the background
python3 app.py