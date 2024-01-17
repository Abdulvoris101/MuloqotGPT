from kombu import Exchange, Queue
from utils import constants
from celery.beat import crontab

broker_url = constants.REDIS_URL
result_backend = constants.REDIS_URL
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Tashkent'

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