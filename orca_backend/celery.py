import os
from celery import Celery
import multiprocessing

# Create a separate process for the worker
multiprocessing.set_start_method('spawn', force=True)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orca_backend.settings')

app = Celery('orca_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(f'django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


def cancel_task(task_id):
    app.control.revoke(task_id, terminate=True, signal="SIGKILL")
