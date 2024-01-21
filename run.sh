#!/bin/bash

alembic upgrade head

rq worker &

# Start scheduler.py in the background
python3 scheduler.py &

# Start your main Python script in the background
python3 app.py