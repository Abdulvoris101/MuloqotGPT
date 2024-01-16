celery -A tasks worker -f logfile.log --loglevel=info  --detach
celery -A tasks beat --loglevel=info --detach
alembic upgrade head
python3 app.py