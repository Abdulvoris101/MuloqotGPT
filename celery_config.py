from kombu import Exchange, Queue
from utils import constants
from celery.beat import crontab
import os
from dotenv import load_dotenv
from celery import Celery


load_dotenv()

broker_url = constants.REDIS_URL
result_backend = constants.REDIS_URL
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Tashkent'

beat_schedule_filename = 'celerybeat-schedule'


celery = Celery(
    'tasks',
    broker=constants.REDIS_URL,
    backend=constants.REDIS_URL,
    include=["tasks"]
)

celery.autodiscover_tasks()

task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
)

celery.conf.beat_schedule = {
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
celery.conf.beat_scheduler = 'celery.beat.PersistentScheduler'
celery.conf.beat_schedule_filename = 'celerybeat-schedule'