#!/bin/bash

alembic upgrade head

nohup rq worker &

mv scheduler/tasks.py .
mv scheduler/scheduler.py .
nohup python3 scheduler.py &

# Start your main Python script in the background
python3 app.py