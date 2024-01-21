from kombu import Exchange, Queue
from utils import constants
from celery.beat import crontab
from celery.beat import PersistentScheduler
import os
from dotenv import load_dotenv

load_dotenv()

broker_url = constants.REDIS_URL
result_backend = constants.REDIS_URL
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Tashkent'

beat_schedule_filename = 'celerybeat-schedule'

task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
)

beat_schedule = {
    'run-task-every-day': {
        'task': 'tasks.cancelExpiredSubscriptions',
        'schedule': crontab(minute=0, hour=0)
    },
    'clear-todays-message': {
        'task': 'tasks.clearAllTodaysMessages',
        'schedule': crontab(minute=0, hour=0)
    },
    'clear-expired-keys': {
        'task': 'tasks.unsetExpiredKeys',
        'schedule': crontab(minute=0, hour=19)
    },
}

postgres_user = os.environ.get("POSTGRES_DB_USER")
postgres_password = os.environ.get("POSTGRES_DB_PASSWORD")

db_url = f'postgresql+psycopg2://{postgres_user}:{postgres_password}@db:5432/muloqotai'

beat_scheduler = 'celery.beat.PersistentScheduler'
beat_schedule_options = {
    'schedule_filename': beat_schedule_filename,
    'max_interval': 5 * 60,  # 5 minutes (300 seconds)
    'store': 'sqlalchemy',
    'url': db_url,  # Adjust accordingly
}